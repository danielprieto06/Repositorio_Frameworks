import 'package:flutter/foundation.dart';
import '../models/food.dart';
import '../models/food_entry.dart';
import '../services/api_client.dart';

// Estado de aplicación de la parte de nutrición:
// catálogo de alimentos, comidas registradas y calorías de hoy.
class NutritionProvider extends ChangeNotifier {
  final ApiClient api;
  NutritionProvider(this.api);

  List<Food> foods = [];
  List<FoodEntry> entries = [];
  double caloriesToday = 0;
  bool loading = false;
  String? error;

  // Nombre del alimento de una comida (la API solo devuelve food_id)
  String foodName(int foodId) {
    for (final food in foods) {
      if (food.id == foodId) return food.name;
    }
    return 'Alimento #$foodId';
  }

  Future<void> load() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      // Las tres peticiones salen a la vez y se espera a que terminen todas
      final results = await Future.wait([
        api.get('/foods/'),
        api.get('/food-entries/'),
        api.get('/food-entries/daily-summary'),
      ]);
      foods = (results[0] as List).map((json) => Food.fromJson(json)).toList();
      entries = (results[1] as List).map((json) => FoodEntry.fromJson(json)).toList();
      caloriesToday = (results[2]['calorias_consumidas'] as num).toDouble();
    } on ApiException catch (e) {
      error = e.message;
    } catch (_) {
      error = 'No se pudo conectar con el servidor';
    }
    loading = false;
    notifyListeners();
  }

  // El total del día lo calcula el backend: se vuelve a pedir tras cada cambio
  Future<void> _refreshSummary() async {
    final summary = await api.get('/food-entries/daily-summary');
    caloriesToday = (summary['calorias_consumidas'] as num).toDouble();
  }

  Future<void> addEntry(Food food, double grams) async {
    final json = await api.post('/food-entries/', {'food_id': food.id, 'quantity_g': grams});
    entries.insert(0, FoodEntry.fromJson(json));
    await _refreshSummary();
    notifyListeners();
  }

  Future<void> removeEntry(FoodEntry entry) async {
    await api.delete('/food-entries/${entry.id}');
    entries.remove(entry);
    await _refreshSummary();
    notifyListeners();
  }

  // Solo administradores: un usuario normal recibiría un 403 del backend
  Future<void> createFood(Map<String, dynamic> data) async {
    final json = await api.post('/foods/', data);
    foods.add(Food.fromJson(json));
    foods.sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
    notifyListeners();
  }
}
