// Refleja el esquema ProgressResponse del backend: una medición de peso y altura
class ProgressEntry {
  final int id;
  final double weight; // kg
  final double height; // cm
  final DateTime createdAt;

  ProgressEntry.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        weight = (json['weight'] as num).toDouble(),
        height = (json['height'] as num).toDouble(),
        createdAt = DateTime.parse(json['created_at']); // texto ISO 8601 → DateTime

  // Mismo cálculo que hace el backend en /progress/latest (altura en metros)
  double get bmi => weight / ((height / 100) * (height / 100));
}
