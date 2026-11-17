import 'package:material_ui/material_ui.dart';
import '../models/food.dart';

// Componente propio: tarjeta de un alimento del catálogo (valores por 100 g).
// Sin estado: pinta lo que recibe y avisa con onAdd cuando se quiere registrar.
class FoodCard extends StatelessWidget {
  final Food food;
  final VoidCallback onAdd; // evento propio: "añádeme a las comidas de hoy"

  const FoodCard({super.key, required this.food, required this.onAdd});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.restaurant),
        title: Text(food.name),
        subtitle: Text(
          '${food.calories.toStringAsFixed(0)} kcal · '
          'P ${food.protein.toStringAsFixed(1)} g · '
          'C ${food.carbohydrates.toStringAsFixed(1)} g · '
          'G ${food.fats.toStringAsFixed(1)} g',
        ),
        trailing: IconButton(
          icon: const Icon(Icons.add_circle_outline),
          tooltip: 'Registrar comida',
          onPressed: onAdd,
        ),
      ),
    );
  }
}
