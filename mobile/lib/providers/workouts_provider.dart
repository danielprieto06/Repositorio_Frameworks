import 'package:flutter/foundation.dart';
import '../models/workout.dart';
import '../services/api_client.dart';

// Estado de aplicación: la lista de entrenamientos del usuario
class WorkoutsProvider extends ChangeNotifier {
  final ApiClient api;
  WorkoutsProvider(this.api);

  // Los tres datos que definen qué debe pintar la pantalla
  List<Workout> items = [];
  bool loading = false;
  String? error;

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners(); // la interfaz pasa a "cargando"
    try {
      final data = await api.get('/workouts/') as List; // ojo a la barra final
      items = data.map((json) => Workout.fromJson(json)).toList();
    } on ApiException catch (e) {
      error = e.message; // mensaje "detail" del backend
    } catch (_) {
      error = 'No se pudo conectar con el servidor';
    }
    loading = false;
    notifyListeners(); // la interfaz pasa a lista / vacío / error
  }

  Future<void> add(String title, String description) async {
    final json = await api.post('/workouts/', {'title': title, 'description': description});
    items.insert(0, Workout.fromJson(json)); // el backend ordena por id descendente
    notifyListeners();
  }

  Future<void> update(Workout workout, String title, String description) async {
    final json = await api.put(
      '/workouts/${workout.id}',
      {'title': title, 'description': description},
    );
    final i = items.indexOf(workout);
    if (i != -1) items[i] = Workout.fromJson(json); // se sustituye por la versión nueva
    notifyListeners();
  }

  Future<void> remove(Workout workout) async {
    await api.delete('/workouts/${workout.id}');
    items.remove(workout);
    notifyListeners();
  }
}
