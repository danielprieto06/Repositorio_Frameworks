import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

// Error propio: guarda el código HTTP y el mensaje "detail" que devuelve FastAPI
class ApiException implements Exception {
  final int status;
  final String message;
  ApiException(this.status, this.message);
}

// Única clase de la app que habla HTTP con FastAPI
class ApiClient {
  // Chrome/Linux: localhost. Emulador Android: 10.0.2.2 apunta al equipo anfitrión.
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000';
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  String? token; // lo rellena SessionProvider al iniciar sesión
  void Function()? onUnauthorized; // qué hacer si el servidor dice "token caducado"

  // Cabeceras de TODAS las peticiones. Si hay token, se añade solo:
  // así se invocan los servicios securizados (Authorization: Bearer ...)
  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<dynamic> get(String path) async =>
      _process(await http.get(_uri(path), headers: _headers));

  Future<dynamic> post(String path, Map<String, dynamic> body) async =>
      _process(await http.post(_uri(path), headers: _headers, body: jsonEncode(body)));

  Future<dynamic> put(String path, Map<String, dynamic> body) async =>
      _process(await http.put(_uri(path), headers: _headers, body: jsonEncode(body)));

  Future<dynamic> patch(String path, Map<String, dynamic> body) async =>
      _process(await http.patch(_uri(path), headers: _headers, body: jsonEncode(body)));

  Future<dynamic> delete(String path) async =>
      _process(await http.delete(_uri(path), headers: _headers));

  // Punto único donde se interpreta la respuesta del servidor
  dynamic _process(http.Response r) {
    // 401 teniendo token = ha caducado (dura 30 min) → cerrar sesión
    if (r.statusCode == 401 && token != null) onUnauthorized?.call();
    if (r.statusCode >= 400) throw ApiException(r.statusCode, _detail(r));
    if (r.body.isEmpty) return null; // 204 No Content (DELETE)
    return jsonDecode(utf8.decode(r.bodyBytes)); // utf8 para tildes y ñ
  }

  // FastAPI devuelve {"detail": "texto"}; en los 422 "detail" es una lista
  String _detail(http.Response r) {
    try {
      final detail = jsonDecode(utf8.decode(r.bodyBytes))['detail'];
      return detail is String ? detail : 'Los datos enviados no son válidos';
    } catch (_) {
      return 'Error ${r.statusCode}';
    }
  }
}
