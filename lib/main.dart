import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:math' as math;
import 'dart:async';

void main() {
  runApp(const GuardianAngelApp());
}

class GuardianAngelApp extends StatefulWidget {
  const GuardianAngelApp({super.key});

  @override
  State<GuardianAngelApp> createState() => _GuardianAngelAppState();
}

class _GuardianAngelAppState extends State<GuardianAngelApp> {
  final ThemeManager _themeManager = ThemeManager();

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _themeManager,
      builder: (context, child) {
        return MaterialApp(
          title: 'Guardian Angel - Healthcare Monitoring',
          debugShowCheckedModeBanner: false,
          theme: _themeManager.lightTheme,
          darkTheme: _themeManager.darkTheme,
          themeMode: _themeManager.themeMode == AppThemeMode.system
              ? ThemeMode.system
              : _themeManager.themeMode == AppThemeMode.light
                  ? ThemeMode.light
                  : ThemeMode.dark,
          home: MainAppWrapper(themeManager: _themeManager),
        );
      },
    );
  }
}

// Main app wrapper with navigation
class MainAppWrapper extends StatefulWidget {
  final ThemeManager themeManager;
  
  const MainAppWrapper({super.key, required this.themeManager});

  @override
  State<MainAppWrapper> createState() => _MainAppWrapperState();
}

class _MainAppWrapperState extends State<MainAppWrapper> {
  int _currentIndex = 0;
  late PageController _pageController;

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: 0); // Start on Home
    _currentIndex = 0;
    
    _screens = [
      const LiveAlertsHome(),
      ProfileScreen(themeManager: widget.themeManager),
    ];
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      backgroundColor: isDark ? HealthColors.darkBackground : HealthColors.lightBackground,
      body: PageView(
        controller: _pageController,
        children: _screens,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              GuardianColors.cardBg.withOpacity(0.8),
              GuardianColors.cardBg,
            ],
          ),
          boxShadow: [
            BoxShadow(
              color: GuardianColors.lightGreen.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: SafeArea(
          child: Container(
            height: 80,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(0, Icons.home, 'Home'),
                _buildNavItem(1, Icons.person, 'Profile'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    final isActive = _currentIndex == index;
    return GestureDetector(
      onTap: () {
        _pageController.animateToPage(
          index,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
        HapticFeedback.lightImpact();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isActive 
              ? GuardianColors.lightGreen.withOpacity(0.1) 
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: isActive 
              ? Border.all(color: GuardianColors.lightGreen.withOpacity(0.3))
              : null,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isActive 
                  ? GuardianColors.lightGreen 
                  : GuardianColors.textSecondary,
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isActive 
                    ? GuardianColors.lightGreen 
                    : GuardianColors.textSecondary,
                fontSize: 10,
                fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Professional Healthcare Design System
class HealthColors {
  // Light Theme - Professional Medical Blue
  static const lightPrimary = Color(0xFF2E7D8F); // Medical Blue
  static const lightSecondary = Color(0xFF4A9EAF); // Lighter Medical Blue
  static const lightAccent = Color(0xFF0056B3); // Deep Trust Blue
  static const lightBackground = Color(0xFFF8FAFB); // Clean White
  static const lightSurface = Color(0xFFFFFFFF); // Pure White
  static const lightCardBg = Color(0xFFFFFFFF); // White Cards
  static const lightTextPrimary = Color(0xFF1A1A1A); // Dark Text
  static const lightTextSecondary = Color(0xFF6B7280); // Gray Text
  static const lightBorder = Color(0xFFE5E7EB); // Light Gray Border
  
  // Dark Theme - Professional Medical Dark
  static const darkPrimary = Color(0xFF4A9EAF); // Bright Medical Blue
  static const darkSecondary = Color(0xFF6BB6C7); // Lighter Blue
  static const darkAccent = Color(0xFF3B82F6); // Bright Blue
  static const darkBackground = Color(0xFF0F1419); // Deep Dark
  static const darkSurface = Color(0xFF1F2937); // Dark Gray
  static const darkCardBg = Color(0xFF374151); // Card Dark Gray
  static const darkTextPrimary = Color(0xFFFFFFFF); // White Text
  static const darkTextSecondary = Color(0xFF9CA3AF); // Light Gray Text
  static const darkBorder = Color(0xFF4B5563); // Dark Border
  
  // Universal Status Colors
  static const emergencyRed = Color(0xFFDC2626); // Medical Emergency
  static const warningAmber = Color(0xFFF59E0B); // Medical Warning
  static const safeGreen = Color(0xFF059669); // Medical Safe
  static const criticalOrange = Color(0xFFEA580C); // Critical Alert
}

// Theme Management
enum AppThemeMode { light, dark, system }

class ThemeManager extends ChangeNotifier {
  static final ThemeManager _instance = ThemeManager._internal();
  factory ThemeManager() => _instance;
  ThemeManager._internal();

  AppThemeMode _themeMode = AppThemeMode.system;
  AppThemeMode get themeMode => _themeMode;

  void setThemeMode(AppThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }

  ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    colorScheme: const ColorScheme.light(
      primary: HealthColors.lightPrimary,
      secondary: HealthColors.lightSecondary,
      tertiary: HealthColors.lightAccent,
      surface: HealthColors.lightSurface,
      background: HealthColors.lightBackground,
      error: HealthColors.emergencyRed,
    ),
    scaffoldBackgroundColor: HealthColors.lightBackground,
    cardColor: HealthColors.lightCardBg,
    fontFamily: 'SF Pro Display',
  );

  ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    colorScheme: const ColorScheme.dark(
      primary: HealthColors.darkPrimary,
      secondary: HealthColors.darkSecondary,
      tertiary: HealthColors.darkAccent,
      surface: HealthColors.darkSurface,
      background: HealthColors.darkBackground,
      error: HealthColors.emergencyRed,
    ),
    scaffoldBackgroundColor: HealthColors.darkBackground,
    cardColor: HealthColors.darkCardBg,
    fontFamily: 'SF Pro Display',
  );
}

// Professional Healthcare UI Components
class HealthButton extends StatefulWidget {
  final String label;
  final IconData? icon;
  final VoidCallback onPressed;
  final bool isPrimary;
  final bool isLoading;

  const HealthButton({
    super.key,
    required this.label,
    this.icon,
    required this.onPressed,
    this.isPrimary = false,
    this.isLoading = false,
  });

  @override
  State<HealthButton> createState() => _HealthButtonState();
}

class _HealthButtonState extends State<HealthButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) => setState(() => _isPressed = false),
      onTapCancel: () => setState(() => _isPressed = false),
      onTap: widget.onPressed,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        decoration: BoxDecoration(
          color: widget.isPrimary
              ? (isDark ? HealthColors.darkPrimary : HealthColors.lightPrimary)
              : (isDark ? HealthColors.darkCardBg : HealthColors.lightCardBg),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: widget.isPrimary
                ? Colors.transparent
                : (isDark ? HealthColors.darkBorder : HealthColors.lightBorder),
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: (widget.isPrimary 
                  ? (isDark ? HealthColors.darkPrimary : HealthColors.lightPrimary)
                  : Colors.black)
                .withOpacity(_isPressed ? 0.3 : 0.1),
              blurRadius: _isPressed ? 8 : 4,
              offset: Offset(0, _isPressed ? 2 : 1),
            ),
          ],
        ),
        child: widget.isLoading
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    widget.isPrimary 
                        ? Colors.white 
                        : (isDark ? HealthColors.darkPrimary : HealthColors.lightPrimary),
                  ),
                ),
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (widget.icon != null) ...[
                    Icon(
                      widget.icon, 
                      size: 18,
                      color: widget.isPrimary 
                          ? Colors.white 
                          : (isDark ? HealthColors.darkTextPrimary : HealthColors.lightTextPrimary),
                    ),
                    const SizedBox(width: 8),
                  ],
                  Flexible(
                    child: Text(
                      widget.label,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: widget.isPrimary 
                            ? Colors.white 
                            : (isDark ? HealthColors.darkTextPrimary : HealthColors.lightTextPrimary),
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

class HealthCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? backgroundColor;

  const HealthCard({
    super.key,
    required this.child,
    this.padding,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Container(
      padding: padding ?? const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: backgroundColor ?? (isDark ? HealthColors.darkCardBg : HealthColors.lightCardBg),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? HealthColors.darkBorder : HealthColors.lightBorder,
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDark ? 0.3 : 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );
  }
}

class StatusIndicator extends StatelessWidget {
  final String status;
  final StatusType type;

  const StatusIndicator({
    super.key,
    required this.status,
    required this.type,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    IconData statusIcon;
    
    switch (type) {
      case StatusType.active:
        statusColor = HealthColors.emergencyRed;
        statusIcon = Icons.warning;
        break;
      case StatusType.resolved:
        statusColor = HealthColors.safeGreen;
        statusIcon = Icons.check_circle;
        break;
      case StatusType.falseAlert:
        statusColor = HealthColors.warningAmber;
        statusIcon = Icons.info;
        break;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(statusIcon, size: 14, color: statusColor),
          const SizedBox(width: 6),
          Text(
            status,
            style: TextStyle(
              color: statusColor,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

// Legacy GuardianColors for backward compatibility (gradually replacing)
class GuardianColors {
  static const lightGreen = HealthColors.lightPrimary;
  static const lightBlue = HealthColors.lightSecondary;
  static const darkBg = HealthColors.darkBackground;
  static const cardBg = HealthColors.darkCardBg;
  static const glowGreen = HealthColors.lightPrimary;
  static const glowBlue = HealthColors.lightSecondary;
  static const emergencyRed = HealthColors.emergencyRed;
  static const warningAmber = HealthColors.warningAmber;
  static const safeGreen = HealthColors.safeGreen;
  static const textPrimary = HealthColors.darkTextPrimary;
  static const textSecondary = HealthColors.darkTextSecondary;
  static const glassBorder = HealthColors.darkBorder;
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
          Flexible(
            child: Column(
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
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  value,
                  style: const TextStyle(
                    color: GuardianColors.textPrimary,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Screen 1: Connect & Pair
class ConnectScreen extends StatefulWidget {
  final bool showBackButton;
  
  const ConnectScreen({
    super.key, 
    this.showBackButton = false,
  });

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
      appBar: widget.showBackButton 
          ? AppBar(
              backgroundColor: Colors.transparent,
              elevation: 0,
              leading: IconButton(
                icon: Icon(
                  Icons.arrow_back, 
                  color: GuardianColors.textPrimary,
                ),
                onPressed: () => Navigator.of(context).pop(),
              ),
              title: const Text(
                'Device Connection Settings',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              automaticallyImplyLeading: false,
            )
          : null,
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
                    HealthCard(
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
                              Expanded(
                                child: Text(
                                  _isConnected ? 'Connected to Home Device' : 'Connect to Home Device',
                                  style: const TextStyle(
                                    color: GuardianColors.textPrimary,
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                  overflow: TextOverflow.ellipsis,
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
                                child: HealthButton(
                                  label: 'Test Connection',
                                  icon: Icons.wifi_find,
                                  onPressed: _testConnection,
                                  isPrimary: false,
                                  isLoading: _isConnecting,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: HealthButton(
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
                                      'Connected to: Home Guardian System\nPatient: Anisha Dhawan',
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
                          children: [
                            Icon(
                              Icons.qr_code_scanner,
                              color: GuardianColors.lightBlue,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Tap to scan QR code for quick setup',
                                style: TextStyle(
                                  color: GuardianColors.textSecondary,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                ),
                                overflow: TextOverflow.ellipsis,
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
          HealthButton(
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
  
  // System state management for Raspberry Pi integration
  bool _hasActiveAlert = false;  // Default: no active alerts
  String _patientName = 'Anisha Dhawan';
  String _patientPhone = '+1 (678) 472-3672';
  String _liveStatus = 'System Ready';  // Default status
  String _systemStatus = 'Connected - Home Guardian System';
  int _camerasOnline = 4;
  String _lastActivity = 'System active - monitoring';
  
  // Demo controls for UGA Hacks presentation
  bool _showDemoControls = true;

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
    _pulseController.repeat(); // Start pulsing since we have an active alert
    // _startEventSimulation(); // Removed for POC - start with active alert
  }

  void _startEventSimulation() {
    // This method will be replaced with real backend integration
    // For now, it's for demo purposes only
  }
  
  // Simulate receiving fall detection alert from Raspberry Pi
  void _simulateFallDetection() {
    if (mounted) {
      setState(() {
        _hasActiveAlert = true;
        _liveStatus = 'Fall Detected';
        _lastActivity = 'Kitchen - Just now';
      });
      _pulseController.repeat();
      HapticFeedback.heavyImpact();
      
      // This is where backend integration would receive:
      // - Fall detection timestamp
      // - Video clip from Raspberry Pi
      // - Confidence score
      // - Location (if multiple cameras)
    }
  }
  
  // Method that will connect to Saachi's backend API
  void _onBackendFallAlert(Map<String, dynamic> alertData) {
    // Future integration point:
    // alertData would contain:
    // - timestamp
    // - videoClipUrl
    // - confidence
    // - cameraLocation
    // - patientId
    
    if (mounted) {
      setState(() {
        _hasActiveAlert = true;
        _liveStatus = 'Fall Detected';
        _lastActivity = '${alertData['location'] ?? 'Unknown'} - Just now';
      });
      _pulseController.repeat();
      HapticFeedback.heavyImpact();
    }
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
                      
                      // Demo Controls (for UGA Hacks presentation)
                      if (_showDemoControls) ...[
                        const SizedBox(height: 32),
                        _buildDemoControls(),
                      ],
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
              
              // Connection status
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: GuardianColors.safeGreen.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: GuardianColors.safeGreen.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: GuardianColors.safeGreen,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _systemStatus,
                      style: const TextStyle(
                        color: GuardianColors.textPrimary,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '• $_camerasOnline cameras',
                      style: const TextStyle(
                        color: GuardianColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 20),
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
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Alert header
          Row(
            children: [
              AnimatedBuilder(
                animation: _pulseController,
                builder: (context, child) {
                  return Icon(
                    Icons.warning_rounded,
                    color: GuardianColors.emergencyRed.withOpacity(
                      0.7 + (_pulseController.value * 0.3)
                    ),
                    size: 32,
                  );
                },
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
                      child: HealthButton(
                        label: 'View Clip',
                        icon: Icons.play_circle_outline,
                        onPressed: _viewClip,
                        isPrimary: true,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: HealthButton(
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
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: steps.asMap().entries.map((entry) {
              final index = entry.key;
              final step = entry.value;
              final isCompleted = step['completed'] as bool;
              
              return SizedBox(
                width: MediaQuery.of(context).size.width / steps.length - 16,
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
        ),
        const SizedBox(height: 8),
        // Step labels
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: steps.map((step) => SizedBox(
              width: MediaQuery.of(context).size.width / steps.length - 16,
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
                overflow: TextOverflow.ellipsis,
              ),
            )).toList(),
          ),
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
    
    return HealthCard(
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
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        maxChildSize: 0.95,
        minChildSize: 0.5,
        builder: (context, scrollController) => Container(
          decoration: const BoxDecoration(
            color: GuardianColors.darkBg,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: const EventDetailScreen(),
        ),
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
            
            HealthButton(
              label: 'Call 911',
              icon: Icons.emergency,
              onPressed: () {
                Navigator.pop(context);
                _simulateEmergencyCall();
              },
              isPrimary: true,
            ),
            
            const SizedBox(height: 12),
            
            HealthButton(
              label: 'Call Anisha',
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
      _liveStatus = 'System Ready';
      _lastActivity = 'System active - monitoring';
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

  Future<void> _makePhoneCall(String phoneNumber, String personName) async {
    // Remove any formatting from phone number for the tel: scheme
    final cleanNumber = phoneNumber.replaceAll(RegExp(r'[^\d+]'), '');
    final Uri phoneLaunchUri = Uri(
      scheme: 'tel',
      path: cleanNumber,
    );
    
    try {
      if (await canLaunchUrl(phoneLaunchUri)) {
        await launchUrl(phoneLaunchUri);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not launch phone call to $personName'),
            backgroundColor: HealthColors.emergencyRed,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error calling $personName: $e'),
          backgroundColor: HealthColors.emergencyRed,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  void _simulatePatientCall() {
    _makePhoneCall(_patientPhone, _patientName);
  }
  
  Widget _buildDemoControls() {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.developer_mode, color: HealthColors.lightSecondary),
              const SizedBox(width: 12),
              const Text(
                'Demo Controls (UGA Hacks)',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Simulate Raspberry Pi fall detection events',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: HealthButton(
                  label: 'Simulate Fall',
                  icon: Icons.warning,
                  onPressed: _hasActiveAlert ? () {} : _simulateFallDetection,
                  isPrimary: !_hasActiveAlert,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: HealthButton(
                  label: 'Clear Alert',
                  icon: Icons.check_circle,
                  onPressed: _hasActiveAlert ? _markResolved : () {},
                  isPrimary: _hasActiveAlert,
                ),
              ),
            ],
          ),
        ],
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
  final double _fallTimestamp = 8.2;
  
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
      body: Column(
        children: [
          // Modal header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Row(
              children: [
                Container(
                  width: 4,
                  height: 30,
                  decoration: BoxDecoration(
                    color: GuardianColors.lightBlue,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Fall Analysis',
                    style: TextStyle(
                      color: GuardianColors.textPrimary,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.share, color: GuardianColors.lightBlue),
                  onPressed: _shareAnalysis,
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: GuardianColors.textSecondary),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading ? _buildLoadingView() : _buildAnalysisView(),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingView() {
    return Expanded(
      child: Center(
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
      ),
    );
  }

  Widget _buildAnalysisView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          _buildVideoPlayer(),
          const SizedBox(height: 24),
          _buildExplainabilityCard(),
          const SizedBox(height: 24),
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildVideoPlayer() {
    return HealthCard(
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
        const SizedBox(height: 16),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildVideoControlButton(
                Icons.replay_10,
                () => _jumpToTime(_currentTime - 10),
              ),
              const SizedBox(width: 24),
              HealthButton(
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
        ),
        const SizedBox(height: 12),
        HealthButton(
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
    return HealthCard(
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
              child: HealthButton(
                label: 'Confirm Fall',
                icon: Icons.warning,
                onPressed: _confirmFall,
                isPrimary: true,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: HealthButton(
                label: 'False Alert',
                icon: Icons.close,
                onPressed: _markFalseAlert,
                isPrimary: false,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        HealthButton(
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
    final clampedTime = math.max(0.0, math.min(_totalTime, time));
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

// Screen 4: Profile/Caregivers (Enterprise look)
class ProfileScreen extends StatefulWidget {
  final ThemeManager? themeManager;
  
  const ProfileScreen({super.key, this.themeManager});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  // Mock caregiver data
  bool _notifyOnFall = true;
  bool _callPrimaryAuto = true;
  bool _messagePrimaryAuto = true;
  bool _notifySecondary = true;
  
  final Map<String, String> _primaryCaregiver = {
    'name': 'Stuti Thummala',
    'phone': '+1 (470) 807-3876',
  };
  
  final Map<String, String> _secondaryCaregiver = {
    'name': 'Saachi Varshney',
    'phone': '+1 (470) 553-6461',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GuardianColors.darkBg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          'Caregivers',
          style: TextStyle(
            color: GuardianColors.textPrimary,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCaregiverCard(
              'Primary Caregiver', 
              _primaryCaregiver, 
              isPrimary: true,
            ),
            const SizedBox(height: 24),
            _buildCaregiverCard(
              'Secondary Caregiver', 
              _secondaryCaregiver, 
              isPrimary: false,
            ),
            const SizedBox(height: 32),
            _buildDeviceSettings(),
            const SizedBox(height: 24),
            if (widget.themeManager != null) ...[
              _buildThemeSettings(),
              const SizedBox(height: 32),
            ],
            _buildNotificationSettings(),
            const SizedBox(height: 32),
            _buildTestSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildCaregiverCard(String title, Map<String, String> caregiver, {required bool isPrimary}) {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isPrimary ? Icons.star : Icons.person_add,
                color: isPrimary ? GuardianColors.lightGreen : GuardianColors.lightBlue,
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: const TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: GuardianColors.cardBg.withOpacity(0.3),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: GuardianColors.glassBorder,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.person,
                      color: GuardianColors.textSecondary,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        caregiver['name']!,
                        style: const TextStyle(
                          color: GuardianColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.phone,
                      color: GuardianColors.textSecondary,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      caregiver['phone']!,
                      style: const TextStyle(
                        color: GuardianColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                HealthButton(
                  label: 'Call ${caregiver['name']!.split(' ')[0]}',
                  icon: Icons.call,
                  onPressed: () => _makePhoneCall(caregiver['phone']!, caregiver['name']!),
                  isPrimary: false,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeviceSettings() {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.router, color: HealthColors.lightPrimary),
              const SizedBox(width: 12),
              const Text(
                'Device Settings',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Manage your Guardian Angel device connection',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          HealthButton(
            label: 'Device Connection Settings',
            icon: Icons.settings,
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const ConnectScreen(showBackButton: true),
                ),
              );
              HapticFeedback.lightImpact();
            },
            isPrimary: false,
          ),
        ],
      ),
    );
  }

  Widget _buildThemeSettings() {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.palette, color: HealthColors.lightPrimary),
              const SizedBox(width: 12),
              const Text(
                'Theme Settings',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Choose your preferred theme mode',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          _buildThemeOption(
            'Light Mode',
            'Clean and bright interface',
            Icons.light_mode,
            AppThemeMode.light,
          ),
          const SizedBox(height: 12),
          _buildThemeOption(
            'Dark Mode',
            'Easy on the eyes in low light',
            Icons.dark_mode,
            AppThemeMode.dark,
          ),
          const SizedBox(height: 12),
          _buildThemeOption(
            'System Default',
            'Follows your device settings',
            Icons.settings_suggest,
            AppThemeMode.system,
          ),
        ],
      ),
    );
  }

  Widget _buildThemeOption(String title, String subtitle, IconData icon, AppThemeMode mode) {
    final isSelected = widget.themeManager?.themeMode == mode;
    
    return GestureDetector(
      onTap: () {
        widget.themeManager?.setThemeMode(mode);
        HapticFeedback.lightImpact();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected 
              ? HealthColors.lightPrimary.withOpacity(0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected 
                ? HealthColors.lightPrimary
                : GuardianColors.glassBorder,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: isSelected 
                  ? HealthColors.lightPrimary
                  : GuardianColors.textSecondary,
              size: 24,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: isSelected 
                          ? HealthColors.lightPrimary
                          : GuardianColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      color: GuardianColors.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: HealthColors.lightPrimary,
                size: 20,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationSettings() {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.notifications, color: GuardianColors.lightBlue),
              const SizedBox(width: 12),
              const Text(
                'Alert Settings',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildToggleSetting(
            'Notify on fall',
            'Send notifications when falls are detected',
            _notifyOnFall,
            (value) => setState(() => _notifyOnFall = value),
          ),
          const SizedBox(height: 16),
          _buildToggleSetting(
            'Call primary automatically',
            'Auto-call primary caregiver on confirmed falls',
            _callPrimaryAuto,
            (value) => setState(() => _callPrimaryAuto = value),
          ),
          const SizedBox(height: 16),
          _buildToggleSetting(
            'Message primary automatically',
            'Send SMS to primary caregiver instantly',
            _messagePrimaryAuto,
            (value) => setState(() => _messagePrimaryAuto = value),
          ),
          const SizedBox(height: 16),
          _buildToggleSetting(
            'Notify secondary on fall',
            'Alert secondary caregiver after 2 minutes',
            _notifySecondary,
            (value) => setState(() => _notifySecondary = value),
          ),
        ],
      ),
    );
  }

  Widget _buildToggleSetting(String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: const TextStyle(
                  color: GuardianColors.textSecondary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
        Transform.scale(
          scale: 0.8,
          child: Switch(
            value: value,
            onChanged: onChanged,
            activeColor: GuardianColors.lightGreen,
            activeTrackColor: GuardianColors.lightGreen.withOpacity(0.3),
            inactiveThumbColor: GuardianColors.textSecondary,
            inactiveTrackColor: GuardianColors.cardBg,
          ),
        ),
      ],
    );
  }

  Widget _buildTestSection() {
    return HealthCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.bug_report, color: GuardianColors.warningAmber),
              const SizedBox(width: 12),
              const Text(
                'Test & Debug',
                style: TextStyle(
                  color: GuardianColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Send test notifications to verify your alert system',
            style: TextStyle(
              color: GuardianColors.textSecondary,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          HealthButton(
            label: 'Send Test Alert',
            icon: Icons.send,
            onPressed: _sendTestAlert,
            isPrimary: true,
          ),
        ],
      ),
    );
  }

  void _sendTestAlert() {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('🚨 Test alert sent to both caregivers'),
        backgroundColor: GuardianColors.lightBlue,
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'VIEW',
          textColor: GuardianColors.textPrimary,
          onPressed: () {
            // Could show test results
          },
        ),
      ),
    );
  }

  Future<void> _makePhoneCall(String phoneNumber, String personName) async {
    // Remove any formatting from phone number for the tel: scheme
    final cleanNumber = phoneNumber.replaceAll(RegExp(r'[^\d+]'), '');
    final Uri phoneLaunchUri = Uri(
      scheme: 'tel',
      path: cleanNumber,
    );
    
    try {
      if (await canLaunchUrl(phoneLaunchUri)) {
        await launchUrl(phoneLaunchUri);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not launch phone call to $personName'),
            backgroundColor: HealthColors.emergencyRed,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error calling $personName: $e'),
          backgroundColor: HealthColors.emergencyRed,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }
}
