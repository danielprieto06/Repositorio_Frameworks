import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../models/exercise.dart';
import '../providers/session_provider.dart';
import '../services/api_client.dart';
import '../utils/run_action.dart';

// Catálogo público de ejercicios con filtro por grupo muscular
class ExercisesScreen extends StatefulWidget {
  const ExercisesScreen({super.key});

  @override
  State<ExercisesScreen> createState() => _ExercisesScreenState();
}

class _ExercisesScreenState extends State<ExercisesScreen> {
  List<Exercise> _items = [];
  bool _loading = true;
  String? _error;
  String _filter = '';
  int _request = 0; // nº de la última petición lanzada

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    // Al escribir rápido salen varias peticiones: solo vale la respuesta de la última
    final request = ++_request;
    setState(() {
      _loading = true;
      _error = null;
    });
    List<Exercise> items = [];
    String? error;
    try {
      // encodeQueryComponent: espacios y tildes viajan bien en la URL
      final query = _filter.isEmpty ? '' : '?muscle_group=${Uri.encodeQueryComponent(_filter)}';
      final data = await context.read<ApiClient>().get('/exercises/$query') as List;
      items = data.map((json) => Exercise.fromJson(json)).toList();
    } on ApiException catch (e) {
      error = e.message;
    } catch (_) {
      error = 'No se pudo conectar con el servidor';
    }
    if (!mounted || request != _request) return; // respuesta antigua: se descarta
    setState(() {
      _items = items;
      _error = error;
      _loading = false;
    });
  }

  // Solo admin: crear un ejercicio (POST /exercises/)
  Future<void> _create() async {
    final api = context.read<ApiClient>();
    final formKey = GlobalKey<FormState>();
    final name = TextEditingController();
    final group = TextEditingController();
    final description = TextEditingController();

    final data = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nuevo ejercicio'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: name,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (v) {
                  final n = v!.trim().length;
                  return n < 1 || n > 100 ? 'Entre 1 y 100 caracteres' : null;
                },
              ),
              TextFormField(
                controller: group,
                decoration: const InputDecoration(labelText: 'Grupo muscular'),
                validator: (v) {
                  final n = v!.trim().length;
                  return n < 1 || n > 50 ? 'Entre 1 y 50 caracteres' : null;
                },
              ),
              TextFormField(
                controller: description,
                decoration: const InputDecoration(labelText: 'Descripción'),
                maxLines: 3,
                validator: (v) => v!.trim().length > 1000 ? 'Máximo 1000 caracteres' : null,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, {
                'name': name.text.trim(),
                'muscle_group': group.text.trim(),
                'description': description.text.trim(),
              });
            },
            child: const Text('Crear'),
          ),
        ],
      ),
    );
    if (data == null || !mounted) return;
    // Si no fuese admin, el backend respondería 403 y se vería en el SnackBar
    if (await runAction(context, () => api.post('/exercises/', data))) _load();
  }

  Future<void> _delete(Exercise exercise) async {
    final api = context.read<ApiClient>();
    if (await runAction(context, () => api.delete('/exercises/${exercise.id}'))) _load();
  }

  @override
  Widget build(BuildContext context) {
    final isAdmin = context.watch<SessionProvider>().isAdmin;

    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: TextField(
              decoration: const InputDecoration(
                labelText: 'Grupo muscular',
                hintText: 'pecho, pierna, espalda…',
                prefixIcon: Icon(Icons.search),
              ),
              // evento onChanged: filtrar mientras se escribe
              onChanged: (text) {
                _filter = text.trim();
                _load();
              },
            ),
          ),
          Expanded(child: _body(isAdmin)),
        ],
      ),
      floatingActionButton: isAdmin
          ? FloatingActionButton(
              onPressed: _create,
              tooltip: 'Nuevo ejercicio',
              child: const Icon(Icons.add),
            )
          : null,
    );
  }

  Widget _body(bool isAdmin) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!),
            TextButton(onPressed: _load, child: const Text('Reintentar')),
          ],
        ),
      );
    }
    if (_items.isEmpty) {
      return Center(
        child: Text(_filter.isEmpty ? 'No hay ejercicios en el catálogo' : 'Sin resultados'),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        itemCount: _items.length,
        itemBuilder: (context, i) {
          final exercise = _items[i];
          return ListTile(
            title: Text(exercise.name),
            subtitle: Text(
              exercise.description.isEmpty
                  ? exercise.muscleGroup
                  : '${exercise.muscleGroup} · ${exercise.description}',
            ),
            // El botón de borrar solo se pinta para administradores
            trailing: isAdmin
                ? IconButton(
                    icon: const Icon(Icons.delete_outline),
                    tooltip: 'Eliminar',
                    onPressed: () => _delete(exercise),
                  )
                : null,
          );
        },
      ),
    );
  }
}
