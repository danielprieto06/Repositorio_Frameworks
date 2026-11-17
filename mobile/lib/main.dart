import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import 'providers/nutrition_provider.dart';
import 'providers/session_provider.dart';
import 'providers/workouts_provider.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'services/api_client.dart';

void main() {
  final api = ApiClient(); // una sola instancia compartida: un solo token
  runApp(
    // Los providers van por encima de toda la app: cualquier pantalla puede leerlos
    MultiProvider(
      providers: [
        Provider<ApiClient>.value(value: api),
        ChangeNotifierProvider(create: (_) => SessionProvider(api)),
        ChangeNotifierProvider(create: (_) => WorkoutsProvider(api)),
        ChangeNotifierProvider(create: (_) => NutritionProvider(api)),
      ],
      child: const FitLifeApp(),
    ),
  );
}

class FitLifeApp extends StatelessWidget {
  const FitLifeApp({super.key});

  @override
  Widget build(BuildContext context) {
    // watch = "reconstrúyeme cuando la sesión cambie"
    final session = context.watch<SessionProvider>();

    return MaterialApp(
      title: 'FitLife',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.teal),
      // La "puerta": sin sesión no se puede llegar a ninguna pantalla privada
      home: session.loading
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : session.isLoggedIn
              ? const HomeScreen()
              : const LoginScreen(),
    );
  }
}
