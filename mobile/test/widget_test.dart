import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fitlife/models/workout.dart';
import 'package:fitlife/widgets/bmi_card.dart';
import 'package:fitlife/widgets/workout_card.dart';

// Envuelve un widget en lo mínimo que necesita para pintarse
Widget wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  // Prueba del componente propio: pinta los datos y avisa al pulsar borrar
  testWidgets('WorkoutCard muestra el entrenamiento y emite onDelete', (tester) async {
    var deleted = false;
    final workout = Workout.fromJson({'id': 1, 'title': 'Pierna', 'description': 'Sentadillas'});

    await tester.pumpWidget(wrap(WorkoutCard(workout: workout, onDelete: () => deleted = true)));

    expect(find.text('Pierna'), findsOneWidget);
    expect(find.text('Sentadillas'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.delete_outline));
    expect(deleted, isTrue);
  });

  // La categoría del IMC cambia según el valor recibido
  testWidgets('BmiCard muestra la categoría correcta', (tester) async {
    final date = DateTime(2026, 11, 17);

    await tester.pumpWidget(wrap(BmiCard(bmi: 22.4, weight: 70, height: 177, date: date)));
    expect(find.text('Peso normal'), findsOneWidget);

    await tester.pumpWidget(wrap(BmiCard(bmi: 27.0, weight: 85, height: 177, date: date)));
    expect(find.text('Sobrepeso'), findsOneWidget);
  });
}
