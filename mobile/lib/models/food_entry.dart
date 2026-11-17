// Refleja el esquema FoodEntryResponse: una comida registrada por el usuario
class FoodEntry {
  final int id;
  final int foodId;
  final double quantityG;
  final double caloriesTotal; // lo calcula el backend: calorías * gramos / 100

  FoodEntry.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        foodId = json['food_id'],
        quantityG = (json['quantity_g'] as num).toDouble(),
        caloriesTotal = (json['calories_total'] as num).toDouble();
}
