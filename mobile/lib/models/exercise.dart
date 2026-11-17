// Refleja el esquema ExerciseResponse del backend
class Exercise {
  final int id;
  final String name;
  final String description;
  final String muscleGroup;

  Exercise.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        name = json['name'],
        description = json['description'],
        muscleGroup = json['muscle_group']; // snake_case en la API, camelCase en Dart
}
