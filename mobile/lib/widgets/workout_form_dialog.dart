import 'package:material_ui/material_ui.dart';
import '../models/workout.dart';

// Diálogo para crear o editar un entrenamiento.
// Devuelve (título, descripción) con Navigator.pop, o null si se cancela.
class WorkoutFormDialog extends StatefulWidget {
  final Workout? initial; // null = crear; con valor = editar

  const WorkoutFormDialog({super.key, this.initial});

  @override
  State<WorkoutFormDialog> createState() => _WorkoutFormDialogState();
}

class _WorkoutFormDialogState extends State<WorkoutFormDialog> {
  final _formKey = GlobalKey<FormState>(); // permite validar todos los campos a la vez
  late final _title = TextEditingController(text: widget.initial?.title ?? '');
  late final _description = TextEditingController(text: widget.initial?.description ?? '');

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    Navigator.pop(context, (_title.text.trim(), _description.text.trim()));
  }

  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.initial == null ? 'Nuevo entrenamiento' : 'Editar entrenamiento'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _title,
              autofocus: true,
              decoration: const InputDecoration(labelText: 'Título'),
              // Mismas reglas que WorkoutCreate: título de 1 a 100 caracteres
              validator: (v) {
                final text = v!.trim();
                if (text.isEmpty) return 'El título es obligatorio';
                if (text.length > 100) return 'Máximo 100 caracteres';
                return null; // null = campo válido
              },
            ),
            TextFormField(
              controller: _description,
              decoration: const InputDecoration(labelText: 'Descripción'),
              maxLines: 3,
              validator: (v) => v!.trim().length > 1000 ? 'Máximo 1000 caracteres' : null,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
        FilledButton(onPressed: _submit, child: const Text('Guardar')),
      ],
    );
  }
}
