import 'package:material_ui/material_ui.dart';
import '../services/api_client.dart';

// Ejecuta una acción contra la API y, si falla, enseña el error en un SnackBar.
// Devuelve true si fue bien. Evita repetir el mismo try/catch en cada pantalla.
Future<bool> runAction(BuildContext context, Future<void> Function() action) async {
  // Se guarda ANTES del await: después la pantalla podría ya no existir
  final messenger = ScaffoldMessenger.of(context);
  try {
    await action();
    return true;
  } on ApiException catch (e) {
    messenger.showSnackBar(SnackBar(content: Text(e.message))); // "detail" del backend
  } catch (_) {
    messenger.showSnackBar(
      const SnackBar(content: Text('No se pudo conectar con el servidor')),
    );
  }
  return false;
}

// Convierte "72,5" o "72.5" en número; null si no es válido
double? parseNumber(String text) => double.tryParse(text.trim().replaceAll(',', '.'));
