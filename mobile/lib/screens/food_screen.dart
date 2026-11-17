import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../models/food.dart';
import '../providers/nutrition_provider.dart';
import '../providers/session_provider.dart';
import '../utils/run_action.dart';
import '../widgets/calories_summary.dart';
import '../widgets/food_card.dart';

class FoodScreen extends StatefulWidget {
  const FoodScreen({super.key});

  @override
  State<FoodScreen> createState() => _FoodScreenState();
}

class _FoodScreenState extends State<FoodScreen> {
  @override
  void initState() {
    super.initState();
    // El provider se lee aquí, sin await de por medio, y se usa después
    final provider = context.read<NutritionProvider>();
    // microtask: no se puede notificar a los oyentes en mitad de un build
    Future.microtask(provider.load);
  }

  // Pregunta los gramos y registra la comida (POST /food-entries/)
  Future<void> _addEntry(Food food) async {
    final provider = context.read<NutritionProvider>();
    final controller = TextEditingController(text: '100');
    final grams = await showDialog<double>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(food.name),
        content: TextField(
          controller: controller,
          autofocus: true,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: const InputDecoration(labelText: 'Cantidad', suffixText: 'g'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () => Navigator.pop(context, parseNumber(controller.text)),
            child: const Text('Registrar'),
          ),
        ],
      ),
    );
    if (grams == null || !mounted) return;
    if (grams <= 0) {
      // Misma regla que FoodEntryCreate: quantity_g > 0
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('La cantidad debe ser mayor que 0')),
      );
      return;
    }
    await runAction(context, () => provider.addEntry(food, grams));
  }

  // Solo admin: crear un alimento del catálogo (POST /foods/)
  Future<void> _createFood() async {
    final provider = context.read<NutritionProvider>();
    final formKey = GlobalKey<FormState>();
    final name = TextEditingController();
    // Un controlador por cada campo numérico, con la clave que espera la API
    final numbers = {
      'calories': TextEditingController(),
      'protein': TextEditingController(),
      'carbohydrates': TextEditingController(),
      'fats': TextEditingController(),
    };
    const labels = {
      'calories': 'Calorías (kcal/100 g)',
      'protein': 'Proteínas (g)',
      'carbohydrates': 'Carbohidratos (g)',
      'fats': 'Grasas (g)',
    };

    final data = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nuevo alimento'),
        content: Form(
          key: formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: name,
                  decoration: const InputDecoration(labelText: 'Nombre'),
                  validator: (v) {
                    final n = v!.trim().length;
                    return n < 1 || n > 80 ? 'Entre 1 y 80 caracteres' : null;
                  },
                ),
                for (final key in numbers.keys)
                  TextFormField(
                    controller: numbers[key],
                    decoration: InputDecoration(labelText: labels[key]),
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    validator: (v) {
                      final n = parseNumber(v!);
                      return n == null || n < 0 ? 'Número mayor o igual que 0' : null;
                    },
                  ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, {
                'name': name.text.trim(),
                for (final key in numbers.keys) key: parseNumber(numbers[key]!.text),
              });
            },
            child: const Text('Crear'),
          ),
        ],
      ),
    );
    if (data == null || !mounted) return;
    await runAction(context, () => provider.createFood(data));
  }

  @override
  Widget build(BuildContext context) {
    final nutrition = context.watch<NutritionProvider>();
    final isAdmin = context.watch<SessionProvider>().isAdmin;

    return Scaffold(
      body: _body(nutrition),
      // El botón de crear alimento solo existe para el rol admin
      floatingActionButton: isAdmin
          ? FloatingActionButton(
              onPressed: _createFood,
              tooltip: 'Nuevo alimento',
              child: const Icon(Icons.add),
            )
          : null,
    );
  }

  Widget _body(NutritionProvider nutrition) {
    if (nutrition.loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (nutrition.error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(nutrition.error!),
            TextButton(onPressed: nutrition.load, child: const Text('Reintentar')),
          ],
        ),
      );
    }
    final titleStyle = Theme.of(context).textTheme.titleMedium;
    return RefreshIndicator(
      onRefresh: nutrition.load,
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: [
          CaloriesSummary(calories: nutrition.caloriesToday),
          const SizedBox(height: 16),
          Text('Comidas registradas', style: titleStyle),
          if (nutrition.entries.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Todavía no has registrado ninguna comida'),
            ),
          for (final entry in nutrition.entries)
            ListTile(
              title: Text(nutrition.foodName(entry.foodId)),
              subtitle: Text(
                '${entry.quantityG.toStringAsFixed(0)} g · '
                '${entry.caloriesTotal.toStringAsFixed(0)} kcal',
              ),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                tooltip: 'Eliminar',
                onPressed: () => runAction(context, () => nutrition.removeEntry(entry)),
              ),
            ),
          const SizedBox(height: 16),
          Text('Alimentos (por 100 g)', style: titleStyle),
          if (nutrition.foods.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('El catálogo está vacío: un administrador debe añadir alimentos'),
            ),
          for (final food in nutrition.foods)
            FoodCard(food: food, onAdd: () => _addEntry(food)),
          const SizedBox(height: 72), // hueco para que el botón flotante no tape nada
        ],
      ),
    );
  }
}
