import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_client.dart';

// Estado de sesión de toda la app: quién soy y con qué token.
// ChangeNotifier = "cuando cambie algo, aviso a los widgets que me escuchan".
class SessionProvider extends ChangeNotifier {
  final ApiClient api;
  final _storage = const FlutterSecureStorage(); // almacén cifrado del dispositivo

  Map<String, dynamic>? user; // respuesta de GET /users/me (id, username, email, role)
  bool loading = true; // true mientras se comprueba si había sesión guardada

  SessionProvider(this.api) {
    api.onUnauthorized = logout; // si la API responde 401, se cierra la sesión
    _restore();
  }

  bool get isLoggedIn => user != null;
  bool get isAdmin => user?['role'] == 'admin';

  // Al abrir la app: ¿hay un token guardado y sigue siendo válido?
  Future<void> _restore() async {
    try {
      api.token = await _storage.read(key: 'token');
      if (api.token != null) user = await api.get('/users/me');
    } catch (_) {
      await logout(); // token caducado o servidor caído: sesión limpia
    }
    loading = false;
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    // El login recibe JSON (esquema UserLogin), no un formulario OAuth2
    final data = await api.post('/users/login', {'email': email, 'password': password});
    api.token = data['access_token'];
    await _storage.write(key: 'token', value: api.token);
    user = await api.get('/users/me'); // primer servicio securizado
    notifyListeners();
  }

  // Registro (POST /users/) y, si va bien, entra directamente con esa cuenta
  Future<void> register(String username, String email, String password) async {
    await api.post('/users/', {'username': username, 'email': email, 'password': password});
    await login(email, password);
  }

  // Vuelve a pedir GET /users/me: p. ej. si un admin se cambia su propio rol
  Future<void> refreshUser() async {
    user = await api.get('/users/me');
    notifyListeners();
  }

  Future<void> logout() async {
    api.token = null;
    user = null;
    notifyListeners(); // primero la interfaz: vuelta inmediata al login
    try {
      await _storage.delete(key: 'token');
    } catch (_) {} // si el almacén falla, la sesión en memoria ya está cerrada
  }
}
