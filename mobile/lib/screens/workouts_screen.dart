import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../models/workout.dart';
import '../providers/workouts_provider.dart';
import '../utils/run_action.dart';
import '../widgets/workout_card.dart';
import '../widgets/workout_form_dialog.dart';

class WorkoutsScreen extends StatefulWidget {
  const WorkoutsScreen({super.key});

  @override
  State<WorkoutsScreen> createState() => _WorkoutsScreenState();
}

class _WorkoutsScreenState extends State<WorkoutsScreen> {
  @override
  void initState() {
    super.initState();
    // El provider se lee aquí, sin await de por medio, y se usa después
    final provider = context.read<WorkoutsProvider>();
    // microtask: no se puede notificar a los oyentes en mitad de un build
    Future.microtask(provider.load);
  }

  // Abre el diálogo y, si se guarda, crea o modifica el entrenamiento
  Future<void> _openForm([Workout? workout]) async {
    final provider = context.read<WorkoutsProvider>();
    final result = await showDialog<(String, String)>(
      context: context,
      builder: (_) => WorkoutFormDialog(initial: workout),
    );
    if (result == null || !mounted) return; // cancelado
    final (title, description) = result;
    await runAction(
      context,
      () => workout == null
          ? provider.add(title, description)
          : provider.update(workout, title, description),
    );
  }

  @override
  Widget build(BuildContext context) {
    final workouts = context.watch<WorkoutsProvider>();

    return Scaffold(
      body: _body(workouts),
      floatingActionButton: FloatingActionButton(
        onPressed: _openForm,
        tooltip: 'Nuevo entrenamiento',
        child: const Icon(Icons.add),
      ),
    );
  }

  // Cuatro interfaces distintas según la respuesta de la API
  Widget _body(WorkoutsProvider workouts) {
    if (workouts.loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (workouts.error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(workouts.error!),
            TextButton(onPressed: workouts.load, child: const Text('Reintentar')),
          ],
        ),
      );
    }
    if (workouts.items.isEmpty) {
      return const Center(child: Text('Todavía no tienes entrenamientos'));
    }
    return RefreshIndicator(
      onRefresh: workouts.load, // evento: arrastrar hacia abajo para recargar
      child: ListView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: workouts.items.length,
        itemBuilder: (context, i) {
          final workout = workouts.items[i];
          return WorkoutCard(
            workout: workout,
            onEdit: () => _openForm(workout),
            onDelete: () => runAction(context, () => workouts.remove(workout)),
          );
        },
      ),
    );
  }
}
