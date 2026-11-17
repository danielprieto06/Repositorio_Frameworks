import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../providers/session_provider.dart';
import '../services/api_client.dart';
import 'register_screen.dart';

// StatefulWidget porque tiene estado propio: si está enviando y si hay un error
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _sending = false; // estado local: solo le importa a esta pantalla
  String? _error;

  Future<void> _submit() async {
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      // read = usar el provider sin suscribirse (estamos en un evento, no en build)
      await context.read<SessionProvider>().login(_email.text.trim(), _password.text);
    } on ApiException catch (e) {
      _error = e.message; // "Correo o contraseña incorrectos" viene del backend
    } catch (_) {
      _error = 'No se pudo conectar con el servidor';
    }
    // Si el login fue bien, esta pantalla ya no existe: por eso se comprueba mounted
    if (mounted) setState(() => _sending = false);
  }

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 360),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.fitness_center, size: 56, color: theme.colorScheme.primary),
                Text('FitLife', style: theme.textTheme.headlineMedium),
                Text('Technology for a healthier life', style: theme.textTheme.bodySmall),
                const SizedBox(height: 24),
                TextField(
                  controller: _email,
                  decoration: const InputDecoration(labelText: 'Correo'),
                  keyboardType: TextInputType.emailAddress,
                ),
                TextField(
                  controller: _password,
                  decoration: const InputDecoration(labelText: 'Contraseña'),
                  obscureText: true,
                  onSubmitted: (_) => _submit(), // evento: pulsar Intro
                ),
                const SizedBox(height: 16),
                // La interfaz cambia según la respuesta de la API
                if (_error != null)
                  Text(_error!, style: TextStyle(color: theme.colorScheme.error)),
                const SizedBox(height: 8),
                FilledButton(
                  onPressed: _sending ? null : _submit, // null = botón desactivado
                  child: Text(_sending ? 'Entrando…' : 'Iniciar sesión'),
                ),
                TextButton(
                  // Navegación: se apila la pantalla de registro encima del login
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const RegisterScreen()),
                  ),
                  child: const Text('Crear una cuenta'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
