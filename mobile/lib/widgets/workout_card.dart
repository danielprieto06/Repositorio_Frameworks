import 'package:material_ui/material_ui.dart';
import '../models/workout.dart';

// Componente propio y reutilizable: una tarjeta de entrenamiento.
// No sabe nada de la API: recibe los datos y avisa hacia arriba con callbacks.
class WorkoutCard extends StatelessWidget {
  final Workout workout; // dato de entrada
  final VoidCallback onDelete; // evento de salida: "me han pulsado borrar"
  final VoidCallback? onEdit; // evento de salida opcional: "me han pulsado editar"

  const WorkoutCard({super.key, required this.workout, required this.onDelete, this.onEdit});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.fitness_center),
        title: Text(workout.title),
        subtitle: workout.description.isEmpty ? null : Text(workout.description),
        onTap: onEdit, // null = la tarjeta no es pulsable
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline),
          tooltip: 'Eliminar',
          onPressed: onDelete, // el componente no decide qué pasa: lo decide quien lo usa
        ),
      ),
    );
  }
}
