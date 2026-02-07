import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import 'dart:async';

void main() {
  runApp(const GuardianAngelApp());
}

class GuardianAngelApp extends StatelessWidget {
  const GuardianAngelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Guardian Angel - Caregiver Dashboard',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: const ColorScheme.dark(
          primary: GuardianColors.lightGreen,
          secondary: GuardianColors.lightBlue,
          surface: GuardianColors.cardBg,
          background: GuardianColors.darkBg,
        ),
        useMaterial3: true,
        fontFamily: 'SF Pro Display',
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
          },
        ),
      ),
      home: const ConnectScreen(),
    );
  }
}

// Premium Design System
class GuardianColors {
  static const lightGreen = Color(0xFF4FFFB8);
  static const lightBlue = Color(0xFF4FC3F7);
  static const darkBg = Color(0xFF0A0E27);
  static const cardBg = Color(0xFF1A1D3A);
  static const glowGreen = Color(0xFF00FF88);
  static const glowBlue = Color(0xFF00D4FF);
  static const emergencyRed = Color(0xFFFF4757);
  static const warningAmber = Color(0xFFFFB347);
  static const safeGreen = Color(0xFF2ED573);
  static const textPrimary = Color(0xFFFFFFFF);
  static const textSecondary = Color(0xFFB0B7C3);
  static const glassBorder = Color(0xFF2A2F54);
}

// Premium UI Components
class GlowButton extends StatefulWidget {
  final String label;
  final IconData? icon;
  final VoidCallback onPressed;
  final bool isPrimary;
  final bool isLoading;

  const GlowButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.isPrimary = true,
    this.isLoading = false,
  });

  @override
  State<GlowButton> createState() => _GlowButtonState();
}

class _GlowButtonState extends State<GlowButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _glowAnimation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    _controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = widget.isPrimary
        ? [GuardianColors.lightGreen, GuardianColors.glowGreen]
        : [GuardianColors.lightBlue, GuardianColors.glowBlue];

    return AnimatedBuilder(
      animation: _glowAnimation,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            boxShadow: [
              BoxShadow(
                color: colors[1].withOpacity(_glowAnimation.value * 0.6),
                blurRadius: 20,
                spreadRadius: 2,
              ),
            ],
          ),
          child: ElevatedButton(
            onPressed: widget.isLoading ? null : widget.onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: colors[0],
              foregroundColor: GuardianColors.darkBg,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(28),
                side: BorderSide(
                  color: colors[1].withOpacity(_glowAnimation.value),
                  width: 2,
                ),
              ),
              elevation: 0,
            ),
            child: widget.isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (widget.icon != null) ...[
                        Icon(widget.icon, size: 20),
                        const SizedBox(width: 8),
                      ],
                      Text(
                        widget.label,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
          ),
        );
      },
    );
  }
}

class GlassCard extends StatelessWidget {
  final Widget child;
  final double blur;
  final EdgeInsetsGeometry? padding;

  const GlassCard({
    super.key,
    required this.child,
    this.blur = 10,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: GuardianColors.glassBorder,
          width: 1,
        ),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            GuardianColors.cardBg.withOpacity(0.8),
            GuardianColors.cardBg.withOpacity(0.4),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: GuardianColors.darkBg.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(20),
        child: child,
      ),
    );
  }
}

class ConfidenceRing extends StatefulWidget {
  final double confidence;
  final double size;

  const ConfidenceRing({
    super.key,
    required this.confidence,
    this.size = 60,
  });

  @override
  State<ConfidenceRing> createState() => _ConfidenceRingState();
}

class _ConfidenceRingState extends State<ConfidenceRing>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _progressAnimation = Tween<double>(begin: 0, end: widget.confidence).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: widget.size,
            height: widget.size,
            child: AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return CircularProgressIndicator(
                  value: _progressAnimation.value,
                  strokeWidth: 4,
                  backgroundColor: GuardianColors.cardBg,
                  color: widget.confidence > 0.7
                      ? GuardianColors.emergencyRed
                      : widget.confidence > 0.4
                          ? GuardianColors.warningAmber
                          : GuardianColors.safeGreen,
                );
              },
            ),
          ),
          Text(
            '${(widget.confidence * 100).toInt()}%',
            style: const TextStyle(
              color: GuardianColors.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}

class StatusPill extends StatelessWidget {
  final String status;
  final StatusType type;

  const StatusPill({
    super.key,
    required this.status,
    required this.type,
  });

  @override
  Widget build(BuildContext context) {
    final colors = _getStatusColors(type);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: colors['bg'],
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors['border']!, width: 1),
        boxShadow: [
          BoxShadow(
            color: colors['glow']!.withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Text(
        status.toUpperCase(),
        style: TextStyle(
          color: colors['text'],
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Map<String, Color> _getStatusColors(StatusType type) {
    switch (type) {
      case StatusType.active:
        return {
          'bg': GuardianColors.emergencyRed.withOpacity(0.2),
          'border': GuardianColors.emergencyRed,
          'text': GuardianColors.emergencyRed,
          'glow': GuardianColors.emergencyRed,
        };
      case StatusType.resolved:
        return {
          'bg': GuardianColors.safeGreen.withOpacity(0.2),
          'border': GuardianColors.safeGreen,
          'text': GuardianColors.safeGreen,
          'glow': GuardianColors.safeGreen,
        };
      case StatusType.falseAlert:
        return {
          'bg': GuardianColors.textSecondary.withOpacity(0.2),
          'border': GuardianColors.textSecondary,
          'text': GuardianColors.textSecondary,
          'glow': GuardianColors.textSecondary,
        };
    }
  }
}

enum StatusType { active, resolved, falseAlert }

class TechReasonChip extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const TechReasonChip({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: GuardianColors.cardBg.withOpacity(0.6),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: GuardianColors.lightBlue.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: GuardianColors.lightBlue,
          ),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: GuardianColors.textSecondary,
                  fontSize: 10,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// Screen 1: Connect & Pair
class ConnectScreen extends StatefulWidget {
  const ConnectScreen({super.key});

  @override
  State<ConnectScreen> createState() => _ConnectScreenState();
}

class _ConnectScreenState extends State<ConnectScreen>
    with TickerProviderStateMixin {
  final TextEditingController _serverController = TextEditingController();
  late AnimationController _waveController;
  bool _isConnecting = false;
  bool _isConnected = false;

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    );
    _waveController.repeat();
    
    // Pre-fill with demo server (can be changed)
    _serverController.text = '192.168.1.100:8080';
  }

  @override
  void dispose() {
    _waveController.dispose();
    _serverController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GuardianColors.darkBg,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              GuardianColors.darkBg,
              GuardianColors.cardBg.withOpacity(0.3),
              GuardianColors.darkBg,
            ],
          ),
        ),
        child: Stack(
          children: [
            // Animated wave background
            _buildWaveBackground(),
            
            // Main content
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Spacer(),
                    
                    // Hero section
                    Column(
                      children: [
                        Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: [
                                GuardianColors.lightGreen,
                                GuardianColors.lightBlue,
                              ],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: GuardianColors.lightGreen.withOpacity(0.4),
                                blurRadius: 30,
                                spreadRadius: 10,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.home_outlined,
                            size: 60,
                            color: GuardianColors.darkBg,
                          ),
                        ),
                        const SizedBox(height: 32),
                        const Text(
                          'Guardian Angel',
                          style: TextStyle(
                            color: GuardianColors.textPrimary,
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Caregiver Dashboard',
                          style: TextStyle(
                            color: GuardianColors.textSecondary,
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 48),
                    
                    // Connection card
                    GlassCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _isConnected ? Icons.check_circle : Icons.home_outlined,
                                color: _isConnected 
                                    ? GuardianColors.safeGreen 
                                    : GuardianColors.lightGreen,
                                size: 24,
                              ),
                              const SizedBox(width: 12),
                              Text(
                                _isConnected ? 'Connected to Home Device' : 'Connect to Home Device',
                                style: const TextStyle(
                                  color: GuardianColors.textPrimary,
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Server input
                          const Text(
                            'Server Address',
                            style: TextStyle(
                              color: GuardianColors.textSecondary,
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Container(
                            decoration: BoxDecoration(
                              color: GuardianColors.darkBg.withOpacity(0.5),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: GuardianColors.glassBorder,
                                width: 1,
                              ),
                            ),
                            child: TextField(
                              controller: _serverController,
                              style: const TextStyle(
                                color: GuardianColors.textPrimary,
                                fontSize: 16,
                              ),
                              decoration: InputDecoration(
                                hintText: 'e.g., 192.168.1.100:8080',
                                hintStyle: TextStyle(
                                  color: GuardianColors.textSecondary.withOpacity(0.6),
                                ),
                                border: InputBorder.none,
                                contentPadding: const EdgeInsets.all(16),
                                prefixIcon: Icon(
                                  Icons.router,
                                  color: GuardianColors.lightBlue,
                                  size: 20,
                                ),
                              ),
                              enabled: !_isConnecting,
                            ),
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Connection buttons
                          Row(
                            children: [
                              Expanded(
                                child: GlowButton(
                                  label: 'Test Connection',
                                  icon: Icons.wifi_find,
                                  onPressed: _testConnection,
                                  isPrimary: false,
                                  isLoading: _isConnecting,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: GlowButton(
                                  label: _isConnected ? 'Continue' : 'Save & Continue',
                                  icon: _isConnected ? Icons.arrow_forward : Icons.save,
                                  onPressed: _isConnected ? _navigateToHome : _saveAndContinue,
                                  isPrimary: true,
                                ),
                              ),
                            ],
                          ),
                          
                          if (_isConnected) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: GuardianColors.safeGreen.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: GuardianColors.safeGreen.withOpacity(0.3),
                                ),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.check_circle,
                                    color: GuardianColors.safeGreen,
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  const Expanded(
                                    child: Text(
                                      'Connected to: Home Guardian System\nPatient: Eleanor Johnson',
                                      style: TextStyle(
                                        color: GuardianColors.textPrimary,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    
                    const Spacer(),
                    
                    // QR Code hint (premium feature)
                    GestureDetector(
                      onTap: _showQRFeature,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: GuardianColors.cardBg.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: GuardianColors.lightBlue.withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.qr_code_scanner,
                              color: GuardianColors.lightBlue,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            const Text(
                              'Tap to scan QR code for quick setup',
                              style: TextStyle(
                                color: GuardianColors.textSecondary,
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWaveBackground() {
    return AnimatedBuilder(
      animation: _waveController,
      builder: (context, child) {
        return CustomPaint(
          size: Size(MediaQuery.of(context).size.width, MediaQuery.of(context).size.height),
          painter: WavePainter(_waveController.value),
        );
      },
    );
  }

  Future<void> _testConnection() async {
    if (_serverController.text.trim().isEmpty) {
      _showError('Please enter a server address');
      return;
    }

    setState(() => _isConnecting = true);
    HapticFeedback.lightImpact();

    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      
      // For demo, always succeed with demo address
      setState(() {
        _isConnected = true;
        _isConnecting = false;
      });
      
      HapticFeedback.heavyImpact();
      _showSuccess('Connected successfully!');
    } catch (e) {
      setState(() => _isConnecting = false);
      _showError('Connection failed. Check address and try again.');
    }
  }

  void _saveAndContinue() async {
    if (_serverController.text.trim().isEmpty) {
      _showError('Please enter a server address');
      return;
    }

    // Save to local storage (in real app)
    // SharedPreferences prefs = await SharedPreferences.getInstance();
    // await prefs.setString('server_address', _serverController.text);
    
    _navigateToHome();
  }

  void _navigateToHome() {
    HapticFeedback.heavyImpact();
    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) => const LiveAlertsHome(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(1.0, 0.0),
              end: Offset.zero,
            ).animate(CurvedAnimation(
              parent: animation,
              curve: Curves.easeOutCubic,
            )),
            child: child,
          );
        },
      ),
    );
  }

  void _showQRFeature() {
    HapticFeedback.lightImpact();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: GuardianColors.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.qr_code_scanner, color: GuardianColors.lightBlue),
            const SizedBox(width: 12),
            const Text(
              'QR Quick Connect',
              style: TextStyle(color: GuardianColors.textPrimary),
            ),
          ],
        ),
        content: const Text(
          'Scan a QR code from your Guardian Angel home device to automatically configure the connection.\n\nThis premium feature would use your camera to scan the code and auto-fill the server address.',
          style: TextStyle(color: GuardianColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Maybe Later'),
          ),
          GlowButton(
            label: 'Coming Soon',
            onPressed: () => Navigator.pop(context),
            isPrimary: false,
          ),
        ],
      ),
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: GuardianColors.emergencyRed,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: GuardianColors.safeGreen,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}

class WavePainter extends CustomPainter {
  final double animationValue;

  WavePainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          GuardianColors.lightGreen.withOpacity(0.1),
          GuardianColors.lightBlue.withOpacity(0.05),
          Colors.transparent,
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final path = Path();
    final waveHeight = 30.0;
    final waveLength = size.width;

    path.moveTo(0, size.height * 0.3);

    for (double x = 0; x <= size.width; x++) {
      final y = size.height * 0.3 +
          math.sin((x / waveLength * 2 * math.pi) + (animationValue * 2 * math.pi)) * waveHeight;
      path.lineTo(x, y);
    }

    path.lineTo(size.width, size.height);
    path.lineTo(0, size.height);
    path.close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// Screen 2: Live Alerts Home (Hero Screen)
class LiveAlertsHome extends StatefulWidget {
  const LiveAlertsHome({super.key});

  @override
  State<LiveAlertsHome> createState() => _LiveAlertsHomeState();
}

class _LiveAlertsHomeState extends State<LiveAlertsHome>
    with TickerProviderStateMixin {
  late AnimationController _glowController;
  late AnimationController _pulseController;
  Timer? _eventTimer;
  
  // Mock data
  bool _hasActiveAlert = false;
  String _patientName = 'Eleanor Johnson';
  String _liveStatus = 'Safe';

  @override
  void initState() {
    super.initState();
    
    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _glowController.repeat(reverse: true);
    _startEventSimulation();
  }

  void _startEventSimulation() {
    // Simulate a fall alert after 5 seconds for demo
    _eventTimer = Timer(const Duration(seconds: 5), () {
      if (mounted) {
        setState(() {
          _hasActiveAlert = true;
          _liveStatus = 'Fall Detected';
        });
        _pulseController.repeat();
        HapticFeedback.heavyImpact();
      }
    });
  }

  @override
  void dispose() {
    _glowController.dispose();
    _pulseController.dispose();
    _eventTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GuardianColors.darkBg,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              GuardianColors.darkBg,
              GuardianColors.cardBg.withOpacity(0.2),
              GuardianColors.darkBg,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Hero section
              _buildHeroSection(),
              
              // Main content
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      // Active Alert Card (only shows if active)
                      if (_hasActiveAlert) ...[
                        _buildActiveAlertCard(),
                        const SizedBox(height: 24),
                      ],
                      
                      // Recent Events
                      _buildRecentEventsSection(),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeroSection() {
    final isEmergency = _hasActiveAlert;
    
    return AnimatedBuilder(
      animation: _glowController,
      builder: (context, child) {
        return Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: isEmergency
                  ? [
                      GuardianColors.emergencyRed.withOpacity(0.1),
                      Colors.transparent,
                    ]
                  : [
                      GuardianColors.safeGreen.withOpacity(0.1),
                      Colors.transparent,
                    ],
            ),
          ),
          child: Column(
            children: [
              // Patient monitoring header
              Row(
                children: [
                  Icon(
                    Icons.monitor_heart,
                    color: GuardianColors.lightBlue,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'Monitoring',
                    style: TextStyle(
                      color: GuardianColors.textSecondary,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 8),
              
              // Patient name
              Row(
                children: [
                  Text(
                    _patientName,
                    style: const TextStyle(
                      color: GuardianColors.textPrimary,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Live status with animated glow
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                decoration: BoxDecoration(
                  color: isEmergency 
                      ? GuardianColors.emergencyRed.withOpacity(0.2)
                      : GuardianColors.safeGreen.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(25),
                  border: Border.all(
                    color: isEmergency 
                        ? GuardianColors.emergencyRed.withOpacity(0.6 + _glowController.value * 0.4)
                        : GuardianColors.safeGreen.withOpacity(0.6 + _glowController.value * 0.4),
                    width: 2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: isEmergency 
                          ? GuardianColors.emergencyRed.withOpacity(_glowController.value * 0.3)
                          : GuardianColors.safeGreen.withOpacity(_glowController.value * 0.2),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: isEmergency ? GuardianColors.emergencyRed : GuardianColors.safeGreen,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      _liveStatus,
                      style: TextStyle(
                        color: isEmergency ? GuardianColors.emergencyRed : GuardianColors.safeGreen,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildActiveAlertCard() {
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, child) {
        return Transform.scale(
          scale: 1.0 + (_pulseController.value * 0.02),
          child: GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Alert header
                Row(
                  children: [
                    Icon(
                      Icons.warning_rounded,
                      color: GuardianColors.emergencyRed,
                      size: 32,
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Fall Detected',
                            style: TextStyle(
                              color: GuardianColors.emergencyRed,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            '2:34 PM • Kitchen Camera',
                            style: TextStyle(
                              color: GuardianColors.textSecondary,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                // Caregiver badges
                const Text(
                  'Response Team',
                  style: TextStyle(
                    color: GuardianColors.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _buildCaregiverBadge('Primary: Sarah', Icons.person, true),
                    const SizedBox(width: 8),
                    _buildCaregiverBadge('Secondary: Mike', Icons.person_outline, false),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Response timeline (judge-impressive feature)
                _buildResponseTimeline(),
                
                const SizedBox(height: 24),
                
                // Action buttons
                Row(
                  children: [
                    Expanded(
                      child: GlowButton(
                        label: 'View Clip',
                        icon: Icons.play_circle_outline,
                        onPressed: _viewClip,
                        isPrimary: true,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: GlowButton(
                        label: 'Call Now',
                        icon: Icons.phone,
                        onPressed: _showCallOptions,
                        isPrimary: false,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                // Mark resolved button
                Center(
                  child: TextButton(
                    onPressed: _markResolved,
                    child: const Text(
                      'Mark Resolved',
                      style: TextStyle(
                        color: GuardianColors.textSecondary,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCaregiverBadge(String label, IconData icon, bool isPrimary) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isPrimary 
            ? GuardianColors.lightGreen.withOpacity(0.2)
            : GuardianColors.cardBg.withOpacity(0.6),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isPrimary 
              ? GuardianColors.lightGreen.withOpacity(0.6)
              : GuardianColors.glassBorder,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: isPrimary ? GuardianColors.lightGreen : GuardianColors.textSecondary,
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: isPrimary ? GuardianColors.lightGreen : GuardianColors.textSecondary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResponseTimeline() {
    final steps = [
      {'title': 'Detected', 'completed': true, 'icon': Icons.sensors},
      {'title': 'Clip saved', 'completed': true, 'icon': Icons.videocam},
      {'title': 'SMS sent', 'completed': true, 'icon': Icons.message},
      {'title': 'Call placed', 'completed': false, 'icon': Icons.phone},
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Response Timeline',
          style: TextStyle(
            color: GuardianColors.textSecondary,
            fontSize: 12,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: steps.asMap().entries.map((entry) {
            final index = entry.key;
            final step = entry.value;
            final isCompleted = step['completed'] as bool;
            
            return Expanded(
              child: Row(
                children: [
                  // Step indicator
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 500),
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: isCompleted 
                          ? GuardianColors.safeGreen 
                          : GuardianColors.cardBg,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: isCompleted 
                            ? GuardianColors.safeGreen 
                            : GuardianColors.glassBorder,
                        width: 2,
                      ),
                    ),
                    child: Icon(
                      isCompleted ? Icons.check : step['icon'] as IconData,
                      size: 12,
                      color: isCompleted 
                          ? GuardianColors.darkBg 
                          : GuardianColors.textSecondary,
                    ),
                  ),
                  
                  // Line connector (except for last item)
                  if (index < steps.length - 1)
                    Expanded(
                      child: Container(
                        height: 2,
                        margin: const EdgeInsets.symmetric(horizontal: 8),
                        decoration: BoxDecoration(
                          color: isCompleted 
                              ? GuardianColors.safeGreen.withOpacity(0.5)
                              : GuardianColors.glassBorder,
                          borderRadius: BorderRadius.circular(1),
                        ),
                      ),
                    ),
                ],
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 8),
        // Step labels
        Row(
          children: steps.map((step) => Expanded(
            child: Text(
              step['title'] as String,
              style: TextStyle(
                color: (step['completed'] as bool) 
                    ? GuardianColors.textPrimary 
                    : GuardianColors.textSecondary,
                fontSize: 10,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          )).toList(),
        ),
      ],
    );
  }

  Widget _buildRecentEventsSection() {
    final events = [
      {
        'type': 'resolved',
        'title': 'False Alert - Kitchen',
        'time': 'Yesterday 11:30 AM',
        'description': 'Motion detected, cat knocked over item',
      },
      {
        'type': 'resolved',
        'title': 'Daily Check Complete',
        'time': 'Yesterday 9:00 AM',
        'description': 'Normal activity patterns detected',
      },
      {
        'type': 'resolved',
        'title': 'Fall Alert - Living Room',
        'time': '2 days ago',
        'description': 'Confirmed fall, assistance provided',
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Events',
          style: TextStyle(
            color: GuardianColors.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        
        ...events.map((event) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _buildEventCard(event),
        )).toList(),
      ],
    );
  }

  Widget _buildEventCard(Map<String, String> event) {
    final statusType = event['type'] == 'resolved' ? StatusType.resolved : StatusType.active;
    
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          // Status indicator
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: statusType == StatusType.resolved 
                  ? GuardianColors.safeGreen.withOpacity(0.2)
                  : GuardianColors.emergencyRed.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              statusType == StatusType.resolved ? Icons.check_circle : Icons.warning,
              color: statusType == StatusType.resolved 
                  ? GuardianColors.safeGreen 
                  : GuardianColors.emergencyRed,
              size: 20,
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Event details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        event['title']!,
                        style: const TextStyle(
                          color: GuardianColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    StatusPill(
                      status: statusType == StatusType.resolved ? 'Resolved' : 'Active',
                      type: statusType,
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  event['time']!,
                  style: const TextStyle(
                    color: GuardianColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  event['description']!,
                  style: const TextStyle(
                    color: GuardianColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _viewClip() {
    HapticFeedback.heavyImpact();
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const EventDetailScreen(),
      ),
    );
  }

  void _showCallOptions() {
    HapticFeedback.lightImpact();
    showModalBottomSheet(
      context: context,
      backgroundColor: GuardianColors.cardBg,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Emergency Call Options',
              style: TextStyle(
                color: GuardianColors.textPrimary,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            
            GlowButton(
              label: 'Call 911',
              icon: Icons.emergency,
              onPressed: () {
                Navigator.pop(context);
                _simulateEmergencyCall();
              },
              isPrimary: true,
            ),
            
            const SizedBox(height: 12),
            
            GlowButton(
              label: 'Call Eleanor',
              icon: Icons.person,
              onPressed: () {
                Navigator.pop(context);
                _simulatePatientCall();
              },
              isPrimary: false,
            ),
            
            const SizedBox(height: 12),
            
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text(
                'Cancel',
                style: TextStyle(color: GuardianColors.textSecondary),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _markResolved() {
    HapticFeedback.heavyImpact();
    setState(() {
      _hasActiveAlert = false;
      _liveStatus = 'Safe';
    });
    _pulseController.stop();
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Alert marked as resolved'),
        backgroundColor: GuardianColors.safeGreen,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _simulateEmergencyCall() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📞 Calling 911...'),
        backgroundColor: GuardianColors.emergencyRed,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _simulatePatientCall() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📞 Calling Eleanor Johnson...'),
        backgroundColor: GuardianColors.lightBlue,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

// Screen 3: Event Detail (Premium Explainability)
class EventDetailScreen extends StatefulWidget {

  @override
  State<PairingScreen> createState() => _PairingScreenState();
}

class _PairingScreenState extends State<PairingScreen> 
    with SingleTickerProviderStateMixin {
  final TextEditingController _codeController = TextEditingController();
  bool _isConnected = false;
  bool _isLoading = false;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeIn),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _connectDevice() async {
    if (_codeController.text.isEmpty) return;
    
    setState(() => _isLoading = true);
    HapticFeedback.mediumImpact();
    
    // Simulate connection delay for realistic feel
    await Future.delayed(const Duration(milliseconds: 1500));
    
    setState(() {
      _isLoading = false;
      _isConnected = true;
    });
    
    HapticFeedback.heavyImpact();
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Device connected successfully!'),
          backgroundColor: Colors.green,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Device Pairing'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return FadeTransition(
            opacity: _fadeAnimation,
            child: ScaleTransition(
              scale: _scaleAnimation,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 500),
                      child: Icon(
                        _isConnected ? Icons.check_circle : Icons.link,
                        key: ValueKey(_isConnected),
                        size: 100,
                        color: _isConnected ? Colors.green : Colors.red,
                      ),
                    ),
                    const SizedBox(height: 32),
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      child: Text(
                        _isConnected 
                          ? 'Connected to Guardian Angel Device' 
                          : 'Enter Device Pairing Code',
                        key: ValueKey(_isConnected),
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(height: 32),
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 400),
                      child: _isConnected ? _buildConnectedView() : _buildDisconnectedView(),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDisconnectedView() {
    return Column(
      key: const ValueKey('disconnected'),
      children: [
        TextField(
          controller: _codeController,
          decoration: InputDecoration(
            labelText: 'Pairing Code',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            prefixIcon: const Icon(Icons.qr_code),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 24, letterSpacing: 4),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 24),
        AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: double.infinity,
          height: 50,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _connectDevice,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: _isLoading ? 0 : 2,
            ),
            child: _isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text('Connect Device', style: TextStyle(fontSize: 16)),
          ),
        ),
      ],
    );
  }

  Widget _buildConnectedView() {
    return Card(
      key: const ValueKey('connected'),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: const BoxDecoration(
                    color: Colors.green,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                const Text(
                  'Device Status: Online',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'Last Check: 2 minutes ago',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  HapticFeedback.lightImpact();
                  setState(() => _isConnected = false);
                  _codeController.clear();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[300],
                  foregroundColor: Colors.black87,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('Disconnect'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class FeedScreen extends StatefulWidget {
  const FeedScreen({super.key});

  @override
  State<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> 
    with AutomaticKeepAliveClientMixin, SingleTickerProviderStateMixin {
  
  @override
  bool get wantKeepAlive => true; // Keep state alive for better performance
  
  late AnimationController _listAnimationController;
  late List<Animation<Offset>> _slideAnimations;
  
  static const List<Map<String, String>> _mockAlerts = [
    {'type': 'Fall Detected', 'time': '2 minutes ago', 'status': 'Active', 'severity': 'High'},
    {'type': 'Device Offline', 'time': '1 hour ago', 'status': 'Resolved', 'severity': 'Medium'},
    {'type': 'Battery Low', 'time': '3 hours ago', 'status': 'Resolved', 'severity': 'Low'},
    {'type': 'Fall Detected', 'time': '5 hours ago', 'status': 'Resolved', 'severity': 'High'},
    {'type': 'System Check', 'time': '1 day ago', 'status': 'Resolved', 'severity': 'Low'},
  ];

  @override
  void initState() {
    super.initState();
    _listAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _slideAnimations = List.generate(
      _mockAlerts.length,
      (index) => Tween<Offset>(
        begin: const Offset(1.0, 0.0),
        end: Offset.zero,
      ).animate(CurvedAnimation(
        parent: _listAnimationController,
        curve: Interval(
          index * 0.1,
          1.0,
          curve: Curves.easeOutCubic,
        ),
      )),
    );
    
    _listAnimationController.forward();
  }

  @override
  void dispose() {
    _listAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Alert Feed'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              HapticFeedback.lightImpact();
              _listAnimationController.reset();
              _listAnimationController.forward();
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.delayed(const Duration(milliseconds: 500));
          _listAnimationController.reset();
          _listAnimationController.forward();
        },
        color: Colors.red,
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: _mockAlerts.length,
          // Optimize ListView performance
          cacheExtent: 20.0,
          physics: const BouncingScrollPhysics(), // iOS-like bounce
          itemBuilder: (context, index) {
            final alert = _mockAlerts[index];
            return SlideTransition(
              position: _slideAnimations[index],
              child: _AlertCard(
                alert: alert,
                onTap: () => _showAlertDetails(context, alert),
              ),
            );
          },
        ),
      ),
    );
  }
  void _showAlertDetails(BuildContext context, Map<String, String> alert) {
    HapticFeedback.lightImpact();
    
    if (alert['type'] == 'Fall Detected') {
      // Navigate to fall detection viewer for fall alerts
      Navigator.push(
        context,
        CupertinoPageRoute(
          builder: (context) => FallDetectionViewer(alert: alert),
        ),
      );
    } else {
      // Show regular dialog for other alerts
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: [
              Icon(
                _getAlertIcon(alert['type']!),
                color: _getSeverityColor(alert['severity']!),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(alert['type']!)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailRow('Time', alert['time']!),
              _buildDetailRow('Status', alert['status']!),
              _buildDetailRow('Severity', alert['severity']!),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 70,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500, color: Colors.grey),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  IconData _getAlertIcon(String type) {
    switch (type) {
      case 'Fall Detected':
        return Icons.warning;
      case 'Device Offline':
        return Icons.wifi_off;
      case 'Battery Low':
        return Icons.battery_alert;
      case 'System Check':
        return Icons.check_circle_outline;
      default:
        return Icons.info;
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity) {
      case 'High':
        return Colors.red;
      case 'Medium':
        return Colors.orange;
      case 'Low':
        return Colors.yellow[700]!;
      default:
        return Colors.grey;
    }
  }
}

// Separate widget for better performance
class _AlertCard extends StatelessWidget {
  final Map<String, String> alert;
  final VoidCallback onTap;

  const _AlertCard({
    required this.alert,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: _getSeverityColor(alert['severity']!).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getAlertIcon(alert['type']!),
                    color: _getSeverityColor(alert['severity']!),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert['type']!,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${alert['time']} • ${alert['status']}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                if (alert['status'] == 'Active') ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Text(
                      'View',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ] else ...[
                  Icon(
                    Icons.check_circle,
                    color: Colors.green[400],
                    size: 20,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  IconData _getAlertIcon(String type) {
    switch (type) {
      case 'Fall Detected':
        return Icons.warning;
      case 'Device Offline':
        return Icons.wifi_off;
      case 'Battery Low':
        return Icons.battery_alert;
      case 'System Check':
        return Icons.check_circle_outline;
      default:
        return Icons.info;
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity) {
      case 'High':
        return Colors.red;
      case 'Medium':
        return Colors.orange;
      case 'Low':
        return Colors.yellow[700]!;
      default:
        return Colors.grey;
    }
  }
}

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> 
    with AutomaticKeepAliveClientMixin, SingleTickerProviderStateMixin {
  
  @override
  bool get wantKeepAlive => true;
  
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeIn),
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController, 
      curve: Curves.easeOutCubic,
    ));
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: ListView(
            padding: const EdgeInsets.all(16),
            physics: const BouncingScrollPhysics(),
            children: [
              _buildProfileHeader(),
              const SizedBox(height: 24),
              _buildMenuSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Hero(
              tag: 'profile-avatar',
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.red[100],
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.person,
                  size: 50,
                  color: Colors.red,
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Guardian Angel User',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'guardian@example.com',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuSection() {
    final menuItems = [
      {
        'icon': Icons.notifications_outlined,
        'activeIcon': Icons.notifications,
        'title': 'Notification Settings',
        'onTap': () => _showNotificationSettings(context),
      },
      {
        'icon': Icons.contact_emergency_outlined,
        'activeIcon': Icons.contact_emergency,
        'title': 'Emergency Contacts',
        'onTap': () => _showEmergencyContacts(context),
      },
      {
        'icon': Icons.security_outlined,
        'activeIcon': Icons.security,
        'title': 'Privacy & Security',
        'onTap': () => _showComingSoon(context, 'Privacy & Security'),
      },
      {
        'icon': Icons.help_outline,
        'activeIcon': Icons.help,
        'title': 'Help & Support',
        'onTap': () => _showComingSoon(context, 'Help & Support'),
      },
    ];

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: menuItems.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;
          return _MenuTile(
            icon: item['icon'] as IconData,
            title: item['title'] as String,
            onTap: item['onTap'] as VoidCallback,
            isLast: index == menuItems.length - 1,
          );
        }).toList(),
      ),
    );
  }

  void _showNotificationSettings(BuildContext context) {
    HapticFeedback.lightImpact();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.notifications, color: Colors.red),
            SizedBox(width: 8),
            Text('Notification Settings'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _SettingsTile(
              title: 'Push Notifications',
              value: true,
              onChanged: (value) => HapticFeedback.selectionClick(),
            ),
            _SettingsTile(
              title: 'SMS Alerts',
              value: true,
              onChanged: (value) => HapticFeedback.selectionClick(),
            ),
            _SettingsTile(
              title: 'Email Alerts',
              value: false,
              onChanged: (value) => HapticFeedback.selectionClick(),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              HapticFeedback.heavyImpact();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Settings saved!'),
                  backgroundColor: Colors.green,
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Save', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showEmergencyContacts(BuildContext context) {
    HapticFeedback.lightImpact();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.contact_emergency, color: Colors.red),
            SizedBox(width: 8),
            Text('Emergency Contacts'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _ContactRow('1. John Doe', '(555) 123-4567', Icons.person),
            _ContactRow('2. Jane Smith', '(555) 987-6543', Icons.person),
            _ContactRow('3. Dr. Johnson', '(555) 456-7890', Icons.medical_services),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue[200]!),
              ),
              child: const Text(
                'These contacts will be automatically notified in case of an emergency.',
                style: TextStyle(fontSize: 12),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Edit', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showComingSoon(BuildContext context, String feature) {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$feature coming soon!'),
        backgroundColor: Colors.blue,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

class _MenuTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final bool isLast;

  const _MenuTile({
    required this.icon,
    required this.title,
    required this.onTap,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.vertical(
        top: const Radius.circular(16),
        bottom: Radius.circular(isLast ? 16 : 0),
      ),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        decoration: BoxDecoration(
          border: isLast ? null : Border(
            bottom: BorderSide(color: Colors.grey[200]!),
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: Colors.red, size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: Colors.grey[400],
            ),
          ],
        ),
      ),
    );
  }
}

class _SettingsTile extends StatefulWidget {
  final String title;
  final bool value;
  final ValueChanged<bool>? onChanged;

  const _SettingsTile({
    required this.title,
    required this.value,
    this.onChanged,
  });

  @override
  State<_SettingsTile> createState() => _SettingsTileState();
}

class _SettingsTileState extends State<_SettingsTile> {
  late bool _value;

  @override
  void initState() {
    super.initState();
    _value = widget.value;
  }

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      title: Text(widget.title),
      value: _value,
      onChanged: (value) {
        setState(() => _value = value);
        widget.onChanged?.call(value);
      },
      activeColor: Colors.red,
      contentPadding: EdgeInsets.zero,
    );
  }
}

class _ContactRow extends StatelessWidget {
  final String name;
  final String phone;
  final IconData icon;

  const _ContactRow(this.name, this.phone, this.icon);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.red),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  phone,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Fall Detection Viewer Screen
class FallDetectionViewer extends StatefulWidget {
  final Map<String, String> alert;

  const FallDetectionViewer({super.key, required this.alert});

  @override
  State<FallDetectionViewer> createState() => _FallDetectionViewerState();
}

class _FallDetectionViewerState extends State<FallDetectionViewer>
    with TickerProviderStateMixin {
  late AnimationController _videoController;
  late AnimationController _loadingController;
  late Animation<double> _progressAnimation;
  
  bool _isLoading = true;
  bool _isPlaying = false;
  double _currentTime = 0.0;
  final double _totalTime = 15.0; // 15 second video
  
  @override
  void initState() {
    super.initState();
    
    _videoController = AnimationController(
      duration: Duration(seconds: _totalTime.toInt()),
      vsync: this,
    );
    
    _loadingController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _loadingController, curve: Curves.easeInOut),
    );
    
    _simulateLoading();
    
    _videoController.addListener(() {
      setState(() {
        _currentTime = _videoController.value * _totalTime;
      });
    });
  }

  void _simulateLoading() async {
    _loadingController.forward();
    await Future.delayed(const Duration(seconds: 1)); // Reduced from 2 seconds
    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _videoController.dispose();
    _loadingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fall Detection Analysis'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () => _showSensorAnalysis(),
          ),
        ],
      ),
      body: _isLoading ? _buildLoadingView() : _buildVideoView(),
      bottomNavigationBar: _isLoading ? null : _buildControls(),
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: Colors.red[50],
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.video_camera_back,
              size: 50,
              color: Colors.red,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Loading Fall Detection Video',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          Container(
            width: 200,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
            child: AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: _progressAnimation.value,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          AnimatedBuilder(
            animation: _progressAnimation,
            builder: (context, child) {
              return Text(
                '${(_progressAnimation.value * 100).toInt()}% Complete',
                style: TextStyle(color: Colors.grey[600]),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildVideoView() {
    return Column(
      children: [
        // Video Player Area
        Expanded(
          child: Container(
            margin: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Simulated video frame
                  AnimatedBuilder(
                    animation: _videoController,
                    builder: (context, child) {
                      return _buildSimulatedVideoFrame();
                    },
                  ),
                  
                  // Play/Pause overlay
                  if (!_isPlaying)
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        shape: BoxShape.circle,
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.play_arrow, size: 40),
                        onPressed: _togglePlayPause,
                      ),
                    ),
                  
                  // Fall detection indicator
                  if (_currentTime > 8 && _currentTime < 10)
                    Positioned(
                      top: 20,
                      left: 20,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.warning, color: Colors.white, size: 16),
                            SizedBox(width: 4),
                            Text(
                              'FALL DETECTED',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSimulatedVideoFrame() {
    // Simulate different scenes based on time
    Color backgroundColor = Colors.grey[800]!;
    String sceneText = "Room Camera View";
    
    if (_currentTime > 8 && _currentTime < 10) {
      backgroundColor = Colors.red[900]!;
      sceneText = "FALL IN PROGRESS";
    } else if (_currentTime > 10) {
      backgroundColor = Colors.orange[800]!;
      sceneText = "Person on Floor";
    }
    
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: backgroundColor,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.videocam,
            size: 60,
            color: Colors.white.withOpacity(0.7),
          ),
          const SizedBox(height: 16),
          Text(
            sceneText,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          Text(
            '${_currentTime.toStringAsFixed(1)}s / ${_totalTime.toInt()}s',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControls() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Progress bar
            Row(
              children: [
                Text(
                  '${_currentTime.toStringAsFixed(0)}s',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                Expanded(
                  child: Slider(
                    value: _currentTime,
                    max: _totalTime,
                    activeColor: Colors.red,
                    onChanged: (value) {
                      setState(() => _currentTime = value);
                      _videoController.value = value / _totalTime;
                      // Don't pause when scrubbing - keep playing if it was playing
                    },
                  ),
                ),
                Text(
                  '${_totalTime.toInt()}s',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
            
            // Control buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildControlButton(
                  Icons.replay_10,
                  'Skip Back',
                  () {
                    final newTime = math.max(0, _currentTime - 10).toDouble();
                    setState(() => _currentTime = newTime);
                    _videoController.value = newTime / _totalTime;
                  },
                ),
                _buildControlButton(
                  _isPlaying ? Icons.pause : Icons.play_arrow,
                  _isPlaying ? 'Pause' : 'Play',
                  _togglePlayPause,
                  isPrimary: true,
                ),
                _buildControlButton(
                  Icons.forward_10,
                  'Skip Forward',
                  () {
                    final newTime = math.min(_totalTime, _currentTime + 10).toDouble();
                    setState(() => _currentTime = newTime);
                    _videoController.value = newTime / _totalTime;
                  },
                ),
              ],
            ),
            
            // Fall Confirmation Section
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Column(
                children: [
                  const Text(
                    'Was this a fall?',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Please confirm if this was an actual fall event',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _confirmFall(true),
                          icon: const Icon(Icons.check, size: 20),
                          label: const Text('Yes, Fall'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _confirmFall(false),
                          icon: const Icon(Icons.close, size: 20),
                          label: const Text('No, False Alert'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey[400],
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton(
    IconData icon,
    String label,
    VoidCallback onPressed, {
    bool isPrimary = false,
    bool isSpecial = false,
  }) {
    Color buttonColor = Colors.grey[100]!;
    Color iconColor = Colors.grey[700]!;
    
    if (isPrimary) {
      buttonColor = Colors.red;
      iconColor = Colors.white;
    } else if (isSpecial) {
      buttonColor = Colors.blue[50]!;
      iconColor = Colors.blue;
    }
    
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: buttonColor,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: IconButton(
            icon: Icon(icon, color: iconColor),
            onPressed: () {
              HapticFeedback.lightImpact();
              onPressed();
            },
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  void _togglePlayPause() {
    setState(() => _isPlaying = !_isPlaying);
    
    if (_isPlaying) {
      _videoController.forward();
    } else {
      _videoController.stop();
    }
  }

  void _confirmFall(bool isFall) {
    HapticFeedback.heavyImpact();
    
    String message;
    Color backgroundColor;
    
    if (isFall) {
      message = 'Fall confirmed. Alert will remain active.';
      backgroundColor = Colors.red;
    } else {
      message = 'False alert noted. Alert will be marked as resolved.';
      backgroundColor = Colors.green;
    }
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: const Duration(seconds: 3),
      ),
    );

    // Auto-close after confirmation
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        Navigator.pop(context);
      }
    });
  }

  void _showSensorAnalysis() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Sensor analysis coming soon!'),
        backgroundColor: Colors.blue,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

// Screen 3: Event Detail (Premium Explainability)
class EventDetailScreen extends StatefulWidget {
  const EventDetailScreen({super.key});

  @override
  State<EventDetailScreen> createState() => _EventDetailScreenState();
}

class _EventDetailScreenState extends State<EventDetailScreen>
    with TickerProviderStateMixin {
  late AnimationController _videoController;
  late AnimationController _loadingController;
  late Animation<double> _progressAnimation;
  
  bool _isLoading = true;
  bool _isPlaying = false;
  double _currentTime = 0.0;
  final double _totalTime = 15.0;
  final double _fallTimestamp = 8.2; // When the fall occurs in the video
  
  // Mock explainability data
  final Map<String, dynamic> _fallData = {
    'confidence': 0.89,
    'hipDropSpeed': 0.23,
    'torsoAngleDeg': 72,
    'lowPostureSeconds': 1.3,
    'avgVisibility': 0.86,
    'rulesMet': 3,
    'rulesTotal': 3,
    'fallTimeOffsetMs': 8200,
  };

  @override
  void initState() {
    super.initState();
    
    _videoController = AnimationController(
      duration: Duration(seconds: _totalTime.toInt()),
      vsync: this,
    );
    
    _loadingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _loadingController, curve: Curves.easeInOut),
    );
    
    _simulateLoading();
    
    _videoController.addListener(() {
      setState(() {
        _currentTime = _videoController.value * _totalTime;
      });
    });
  }

  void _simulateLoading() async {
    _loadingController.forward();
    await Future.delayed(const Duration(milliseconds: 1500));
    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _videoController.dispose();
    _loadingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GuardianColors.darkBg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: GuardianColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Fall Analysis',
          style: TextStyle(
            color: GuardianColors.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.share, color: GuardianColors.lightBlue),
            onPressed: _shareAnalysis,
          ),
        ],
      ),
      body: _isLoading ? _buildLoadingView() : _buildAnalysisView(),
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [GuardianColors.lightGreen, GuardianColors.lightBlue],
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: GuardianColors.lightGreen.withOpacity(0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: const Icon(
              Icons.analytics,
              size: 60,
              color: GuardianColors.darkBg,
            ),
          ),
          const SizedBox(height: 32),
          const Text(
            'Analyzing Fall Event',
            style: TextStyle(
              color: GuardianColors.textPrimary,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Processing video and sensor data...',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 32),
          Container(
            width: 250,
            height: 6,
            decoration: BoxDecoration(
              color: GuardianColors.cardBg,
              borderRadius: BorderRadius.circular(3),
            ),
            child: AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: _progressAnimation.value,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [GuardianColors.lightGreen, GuardianColors.lightBlue],
                      ),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          // Video Player Section
          _buildVideoPlayer(),
          
          const SizedBox(height: 24),
          
          // Explainability Card (The Technical "Why")
          _buildExplainabilityCard(),
          
          const SizedBox(height: 24),
          
          // Action buttons
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildVideoPlayer() {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.videocam, color: GuardianColors.lightBlue),
              const SizedBox(width: 12),
              const Text(
                'Fall Detection Video',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Video container
          Container(
            width: double.infinity,
            height: 200,
            decoration: BoxDecoration(
              color: GuardianColors.darkBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: GuardianColors.glassBorder),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  _buildSimulatedVideo(),
                  
                  // Play/Pause overlay
                  if (!_isPlaying)
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: GuardianColors.lightGreen.withOpacity(0.9),
                        shape: BoxShape.circle,
                      ),
                      child: IconButton(
                        icon: const Icon(
                          Icons.play_arrow,
                          color: GuardianColors.darkBg,
                          size: 30,
                        ),
                        onPressed: _togglePlayPause,
                      ),
                    ),
                  
                  // Fall detection overlay
                  if (_currentTime >= _fallTimestamp - 0.5 && _currentTime <= _fallTimestamp + 2)
                    Positioned(
                      top: 16,
                      right: 16,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: GuardianColors.emergencyRed,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          'FALL DETECTED',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Video controls
          _buildVideoControls(),
        ],
      ),
    );
  }

  Widget _buildSimulatedVideo() {
    String sceneDescription = "Kitchen Camera - Normal Activity";
    Color bgColor = GuardianColors.cardBg;
    
    if (_currentTime >= _fallTimestamp - 1 && _currentTime < _fallTimestamp) {
      sceneDescription = "Pre-fall Movement Detected";
      bgColor = GuardianColors.warningAmber.withOpacity(0.3);
    } else if (_currentTime >= _fallTimestamp && _currentTime < _fallTimestamp + 2) {
      sceneDescription = "FALL IN PROGRESS";
      bgColor = GuardianColors.emergencyRed.withOpacity(0.3);
    } else if (_currentTime >= _fallTimestamp + 2) {
      sceneDescription = "Person on Floor - No Movement";
      bgColor = GuardianColors.emergencyRed.withOpacity(0.2);
    }
    
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: double.infinity,
      height: double.infinity,
      color: bgColor,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.videocam,
            size: 40,
            color: GuardianColors.textSecondary,
          ),
          const SizedBox(height: 8),
          Text(
            sceneDescription,
            style: const TextStyle(
              color: GuardianColors.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
          Text(
            '${_currentTime.toStringAsFixed(1)}s',
            style: const TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoControls() {
    return Column(
      children: [
        // Progress bar with markers
        Stack(
          children: [
            SliderTheme(
              data: SliderThemeData(
                trackHeight: 4,
                thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
                overlayShape: const RoundSliderOverlayShape(overlayRadius: 16),
                activeTrackColor: GuardianColors.lightGreen,
                inactiveTrackColor: GuardianColors.cardBg,
                thumbColor: GuardianColors.lightGreen,
              ),
              child: Slider(
                value: _currentTime,
                max: _totalTime,
                onChanged: (value) {
                  setState(() => _currentTime = value);
                  _videoController.value = value / _totalTime;
                },
              ),
            ),
            
            // Fall marker
            Positioned(
              left: (_fallTimestamp / _totalTime) * (MediaQuery.of(context).size.width - 48) + 24,
              top: -2,
              child: Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: GuardianColors.emergencyRed,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Control buttons
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildVideoControlButton(
              Icons.replay_10,
              () => _jumpToTime(_currentTime - 10),
            ),
            const SizedBox(width: 24),
            GlowButton(
              label: _isPlaying ? 'Pause' : 'Play',
              icon: _isPlaying ? Icons.pause : Icons.play_arrow,
              onPressed: _togglePlayPause,
              isPrimary: true,
            ),
            const SizedBox(width: 24),
            _buildVideoControlButton(
              Icons.forward_10,
              () => _jumpToTime(_currentTime + 10),
            ),
          ],
        ),
        
        const SizedBox(height: 12),
        
        // Replay key moment button
        GlowButton(
          label: 'Replay Key Moment',
          icon: Icons.replay,
          onPressed: () => _jumpToTime(_fallTimestamp - 1),
          isPrimary: false,
        ),
      ],
    );
  }

  Widget _buildVideoControlButton(IconData icon, VoidCallback onPressed) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: GuardianColors.cardBg,
        shape: BoxShape.circle,
        border: Border.all(color: GuardianColors.glassBorder),
      ),
      child: IconButton(
        icon: Icon(icon, color: GuardianColors.textPrimary),
        onPressed: onPressed,
      ),
    );
  }

  Widget _buildExplainabilityCard() {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: GuardianColors.lightBlue),
              const SizedBox(width: 12),
              const Text(
                'Why this was flagged',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          const Text(
            'AI analysis detected multiple fall indicators:',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Technical reasons with visual structure
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              TechReasonChip(
                label: 'Hip drop speed',
                value: '+${_fallData['hipDropSpeed']} y/0.4s (fast)',
                icon: Icons.speed,
              ),
              TechReasonChip(
                label: 'Torso angle',
                value: '${_fallData['torsoAngleDeg']}° (near horizontal)',
                icon: Icons.rotate_90_degrees_cw,
              ),
              TechReasonChip(
                label: 'Duration',
                value: '${_fallData['lowPostureSeconds']}s on floor',
                icon: Icons.timer,
              ),
              TechReasonChip(
                label: 'Visibility',
                value: '${(_fallData['avgVisibility'] * 100).toInt()}% avg',
                icon: Icons.visibility,
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Rule triggers
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: GuardianColors.emergencyRed.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: GuardianColors.emergencyRed.withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.rule,
                  color: GuardianColors.emergencyRed,
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Rule triggers met: ${_fallData['rulesMet']}/${_fallData['rulesTotal']}',
                    style: const TextStyle(
                      color: GuardianColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                ConfidenceRing(
                  confidence: _fallData['confidence'],
                  size: 50,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Decision summary
          Row(
            children: [
              Icon(
                Icons.check_circle,
                color: GuardianColors.emergencyRed,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                'Decision: Fall likely',
                style: TextStyle(
                  color: GuardianColors.emergencyRed,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: GlowButton(
                label: 'Confirm Fall',
                icon: Icons.warning,
                onPressed: _confirmFall,
                isPrimary: true,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: GlowButton(
                label: 'False Alert',
                icon: Icons.close,
                onPressed: _markFalseAlert,
                isPrimary: false,
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        GlowButton(
          label: 'Call Emergency Services',
          icon: Icons.phone,
          onPressed: _callEmergencyServices,
          isPrimary: true,
        ),
      ],
    );
  }

  void _togglePlayPause() {
    setState(() => _isPlaying = !_isPlaying);
    HapticFeedback.lightImpact();
    
    if (_isPlaying) {
      _videoController.forward();
    } else {
      _videoController.stop();
    }
  }

  void _jumpToTime(double time) {
    final clampedTime = math.max(0, math.min(_totalTime, time));
    setState(() => _currentTime = clampedTime);
    _videoController.value = clampedTime / _totalTime;
    HapticFeedback.lightImpact();
  }

  void _confirmFall() {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Fall confirmed. Emergency protocols activated.'),
        backgroundColor: GuardianColors.emergencyRed,
        behavior: SnackBarBehavior.floating,
      ),
    );
    Navigator.pop(context);
  }

  void _markFalseAlert() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Marked as false alert. System will learn from this.'),
        backgroundColor: GuardianColors.safeGreen,
        behavior: SnackBarBehavior.floating,
      ),
    );
    Navigator.pop(context);
  }

  void _callEmergencyServices() {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📞 Calling 911...'),
        backgroundColor: GuardianColors.emergencyRed,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _shareAnalysis() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Analysis report shared with care team'),
        backgroundColor: GuardianColors.lightBlue,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
