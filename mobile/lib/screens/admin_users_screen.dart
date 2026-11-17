import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../providers/session_provider.dart';
import '../services/api_client.dart';
import '../utils/run_action.dart';

// Solo para administradores: lista de usuarios y cambio de rol.
// Usa GET /users/admin/users y PATCH /users/admin/users/{id}/role (require_admin).
class AdminUsersScreen extends StatefulWidget {
  const AdminUsersScreen({super.key});

  @override
  State<AdminUsersScreen> createState() => _AdminUsersScreenState();
}

class _AdminUsersScreenState extends State<AdminUsersScreen> {
  List<Map<String, dynamic>> _users = []; // UserResponse: id, username, email, role
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final api = context.read<ApiClient>();
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await api.get('/users/admin/users') as List;
      _users = List<Map<String, dynamic>>.from(data);
    } on ApiException catch (e) {
      _error = e.message; // un usuario normal recibiría aquí el 403 del backend
    } catch (_) {
      _error = 'No se pudo conectar con el servidor';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _changeRole(Map<String, dynamic> user, String role) async {
    final api = context.read<ApiClient>();
    final session = context.read<SessionProvider>();
    // Si es el último admin, el backend responde 409 y runAction lo enseña en un SnackBar
    await runAction(context, () async {
      final updated = await api.patch('/users/admin/users/${user['id']}/role', {'role': role});
      if (!mounted) return;
      setState(() => _users[_users.indexOf(user)] = updated);
      // Si me he quitado el admin a mí mismo, la interfaz tiene que cambiar ya
      if (user['id'] == session.user?['id']) await session.refreshUser();
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!),
            TextButton(onPressed: _load, child: const Text('Reintentar')),
          ],
        ),
      );
    }
    final myId = context.watch<SessionProvider>().user?['id'];

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        itemCount: _users.length,
        itemBuilder: (context, i) {
          final user = _users[i];
          final String username = user['username'];
          return ListTile(
            leading: CircleAvatar(child: Text(username[0].toUpperCase())),
            title: Text(user['id'] == myId ? '$username (tú)' : username),
            subtitle: Text(user['email']),
            trailing: DropdownButton<String>(
              value: user['role'],
              items: const [
                DropdownMenuItem(value: 'user', child: Text('user')),
                DropdownMenuItem(value: 'admin', child: Text('admin')),
              ],
              // evento onChanged: el admin elige otro rol en el desplegable
              onChanged: (role) {
                if (role != null && role != user['role']) _changeRole(user, role);
              },
            ),
          );
        },
      ),
    );
  }
}
