import 'package:material_ui/material_ui.dart';

// Componente propio: las calorías de hoy en grande (GET /food-entries/daily-summary)
class CaloriesSummary extends StatelessWidget {
  final double calories; // "calorias_consumidas" de la API
  final double goal; // objetivo diario orientativo; solo sirve para la barra

  const CaloriesSummary({super.key, required this.calories, this.goal = 2000});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      color: theme.colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Calorías de hoy', style: theme.textTheme.titleSmall),
            Text('${calories.toStringAsFixed(0)} kcal', style: theme.textTheme.displaySmall),
            const SizedBox(height: 8),
            // clamp: si se pasa del objetivo, la barra se queda llena (valor entre 0 y 1)
            LinearProgressIndicator(value: (calories / goal).clamp(0.0, 1.0).toDouble()),
          ],
        ),
      ),
    );
  }
}
