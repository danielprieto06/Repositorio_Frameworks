import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../providers/session_provider.dart';
import 'admin_users_screen.dart';
import 'exercises_screen.dart';
import 'food_screen.dart';
import 'progress_screen.dart';
import 'workouts_screen.dart';

// Zona privada: barra superior común y navegación inferior entre secciones
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0; // estado local: qué pestaña está seleccionada

  @override
  Widget build(BuildContext context) {
    final session = context.watch<SessionProvider>();

    // Las pestañas dependen del rol: la de usuarios solo existe para admin
    final screens = [
      const WorkoutsScreen(),
      const FoodScreen(),
      const ProgressScreen(),
      const ExercisesScreen(),
      if (session.isAdmin) const AdminUsersScreen(),
    ];
    final destinations = [
      const NavigationDestination(icon: Icon(Icons.fitness_center), label: 'Entrenos'),
      const NavigationDestination(icon: Icon(Icons.restaurant), label: 'Comidas'),
      const NavigationDestination(icon: Icon(Icons.monitor_weight), label: 'Progreso'),
      const NavigationDestination(icon: Icon(Icons.menu_book), label: 'Ejercicios'),
      if (session.isAdmin)
        const NavigationDestination(icon: Icon(Icons.admin_panel_settings), label: 'Usuarios'),
    ];
    // Si se pierde el rol estando en "Usuarios", esa pestaña desaparece: vuelta a la primera
    final index = _index < screens.length ? _index : 0;

    return Scaffold(
      appBar: AppBar(
        title: Text('Hola, ${session.user?['username']}'),
        actions: [
          // La interfaz se adapta al rol que devolvió GET /users/me
          if (session.isAdmin) const Chip(label: Text('admin')),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
            onPressed: session.logout,
          ),
        ],
      ),
      body: screens[index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (i) => setState(() => _index = i), // evento → estado → repintado
        destinations: destinations,
      ),
    );
  }
}
