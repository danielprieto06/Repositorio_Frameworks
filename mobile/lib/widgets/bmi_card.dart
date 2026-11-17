import 'package:material_ui/material_ui.dart';
import '../utils/format.dart';

// Componente propio: la última medición con su IMC y la categoría en color.
// Sin estado y sin API: recibe los datos ya calculados por el backend.
class BmiCard extends StatelessWidget {
  final double bmi;
  final double weight;
  final double height;
  final DateTime date;

  const BmiCard({
    super.key,
    required this.bmi,
    required this.weight,
    required this.height,
    required this.date,
  });

  // Categoría según la clasificación de la OMS. Devuelve un record (texto, color)
  (String, Color) get category {
    if (bmi < 18.5) return ('Bajo peso', Colors.blue);
    if (bmi < 25) return ('Peso normal', Colors.green);
    if (bmi < 30) return ('Sobrepeso', Colors.orange);
    return ('Obesidad', Colors.red);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (label, color) = category; // se desestructura el record

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Última medición', style: theme.textTheme.titleSmall),
            Row(
              children: [
                Text('IMC ${bmi.toStringAsFixed(1)}', style: theme.textTheme.displaySmall),
                const SizedBox(width: 12),
                Chip(
                  label: Text(label),
                  backgroundColor: color.withAlpha(40), // el mismo color, muy suave
                  side: BorderSide(color: color),
                ),
              ],
            ),
            Text(
              '${weight.toStringAsFixed(1)} kg · ${height.toStringAsFixed(0)} cm · '
              '${formatDate(date)}',
            ),
          ],
        ),
      ),
    );
  }
}
