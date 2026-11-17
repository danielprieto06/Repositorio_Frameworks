// Refleja el esquema WorkoutResponse del backend (schemas.py)
class Workout {
  final int id;
  final String title;
  final String description;

  // Constructor que convierte el JSON de la API en un objeto Dart
  Workout.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        title = json['title'],
        description = json['description'];
}
