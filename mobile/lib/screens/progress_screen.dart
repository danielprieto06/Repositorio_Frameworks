import 'package:material_ui/material_ui.dart';
import 'package:provider/provider.dart';
import '../models/progress_entry.dart';
import '../services/api_client.dart';
import '../utils/format.dart';
import '../utils/run_action.dart';
import '../widgets/bmi_card.dart';

// Pantalla con estado LOCAL (setState): estos datos no los necesita nadie más
class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key});

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> {
  final _formKey = GlobalKey<FormState>();
  final _weight = TextEditingController();
  final _height = TextEditingController();

  Map<String, dynamic>? _latest; // GET /progress/latest (claves en español)
  List<ProgressEntry> _history = []; // GET /progress/ (más reciente primero)
  bool _loading = true;
  bool _sending = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final api = context.read<ApiClient>(); // antes del primer await
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      try {
        _latest = await api.get('/progress/latest');
      } on ApiException catch (e) {
        // 404 no es un fallo: significa "todavía no hay mediciones" → interfaz vacía
        if (e.status != 404) rethrow; // cualquier otro error sube al try de fuera
        _latest = null;
      }
      final data = await api.get('/progress/') as List;
      _history = data.map((json) => ProgressEntry.fromJson(json)).toList();
    } on ApiException catch (e) {
      _error = e.message;
    } catch (_) {
      _error = 'No se pudo conectar con el servidor';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final api = context.read<ApiClient>();
    setState(() => _sending = true);
    final ok = await runAction(
      context,
      () => api.post('/progress/', {
        'weight': parseNumber(_weight.text),
        'height': parseNumber(_height.text),
      }),
    );
    if (!mounted) return;
    setState(() => _sending = false);
    if (ok) {
      _weight.clear();
      _height.clear();
      await _load(); // el IMC lo calcula el backend: se vuelve a pedir
    }
  }

  @override
  void dispose() {
    _weight.dispose();
    _height.dispose();
    super.dispose();
  }

  // Validador compartido por los dos campos (ProgressCreate: valores > 0)
  String? _positive(String? v) {
    final n = parseNumber(v!);
    return n == null || n <= 0 ? 'Número mayor que 0' : null;
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
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // La tarjeta cambia según la respuesta: 404 → mensaje, 200 → BmiCard
        if (_latest == null)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('Todavía no hay mediciones registradas'),
            ),
          )
        else
          BmiCard(
            bmi: (_latest!['imc'] as num).toDouble(),
            weight: (_latest!['peso'] as num).toDouble(),
            height: (_latest!['altura'] as num).toDouble(),
            date: DateTime.parse(_latest!['fecha']),
          ),
        const SizedBox(height: 24),
        Text('Nueva medición', style: theme.textTheme.titleMedium),
        Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _weight,
                decoration: const InputDecoration(labelText: 'Peso', suffixText: 'kg'),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                validator: _positive,
              ),
              TextFormField(
                controller: _height,
                decoration: const InputDecoration(labelText: 'Altura', suffixText: 'cm'),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                validator: _positive,
                onFieldSubmitted: (_) => _submit(),
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: _sending ? null : _submit,
                child: Text(_sending ? 'Guardando…' : 'Guardar medición'),
              ),
            ],
          ),
        ),
        if (_history.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text('Historial', style: theme.textTheme.titleMedium),
          for (final entry in _history)
            ListTile(
              leading: const Icon(Icons.monitor_weight_outlined),
              title: Text(
                '${entry.weight.toStringAsFixed(1)} kg · ${entry.height.toStringAsFixed(0)} cm',
              ),
              subtitle: Text(formatDate(entry.createdAt)),
              trailing: Text('IMC ${entry.bmi.toStringAsFixed(1)}'),
            ),
        ],
      ],
    );
  }
}
