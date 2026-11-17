// Refleja el esquema FoodResponse del backend. Los valores son por cada 100 g.
class Food {
  final int id;
  final String name;
  final double calories;
  final double protein;
  final double carbohydrates;
  final double fats;

  // "as num" + toDouble(): JSON puede traer 52 (int) o 52.5 (double)
  Food.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        name = json['name'],
        calories = (json['calories'] as num).toDouble(),
        protein = (json['protein'] as num).toDouble(),
        carbohydrates = (json['carbohydrates'] as num).toDouble(),
        fats = (json['fats'] as num).toDouble();
}
