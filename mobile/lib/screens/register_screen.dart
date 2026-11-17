import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../providers/session_provider.dart';
import '../services/api_client.dart';

// Registro contra POST /users/. Repite en el cliente las reglas de UserCreate.
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _sending = false;
  String? _error;

  Future<void> _submit() async {
    // Validar ANTES de llamar a la API: se ahorra una petición que daría 422
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      await context
          .read<SessionProvider>()
          .register(_username.text.trim(), _email.text.trim(), _password.text);
      // Ya hay sesión: se quita esta pantalla y debajo está la app
      if (mounted) Navigator.pop(context);
      return;
    } on ApiException catch (e) {
      _error = e.message; // p. ej. el 409 "El correo electrónico ya está registrado"
    } catch (_) {
      _error = 'No se pudo conectar con el servidor';
    }
    if (mounted) setState(() => _sending = false);
  }

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crear cuenta')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 360),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: _username,
                    decoration: const InputDecoration(labelText: 'Nombre de usuario'),
                    validator: (v) {
                      final n = v!.trim().length;
                      return n < 3 || n > 30 ? 'Entre 3 y 30 caracteres' : null;
                    },
                  ),
                  TextFormField(
                    controller: _email,
                    decoration: const InputDecoration(labelText: 'Correo'),
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) => v!.contains('@') ? null : 'Correo no válido',
                  ),
                  TextFormField(
                    controller: _password,
                    decoration: const InputDecoration(labelText: 'Contraseña'),
                    obscureText: true,
                    validator: (v) => v!.length < 8 ? 'Mínimo 8 caracteres' : null,
                    onFieldSubmitted: (_) => _submit(),
                  ),
                  const SizedBox(height: 16),
                  if (_error != null)
                    Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  const SizedBox(height: 8),
                  FilledButton(
                    onPressed: _sending ? null : _submit,
                    child: Text(_sending ? 'Creando…' : 'Registrarme'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
