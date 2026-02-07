import 'package:flutter/material.dart';

void main() {
  runApp(const GuardianAngelApp());
}

class GuardianAngelApp extends StatelessWidget {
  const GuardianAngelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Guardian Angel - Fall Alert',
      theme: ThemeData(
        primarySwatch: Colors.red,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const PairingScreen(),
    const FeedScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.link),
            label: 'Pairing',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications),
            label: 'Alerts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class PairingScreen extends StatefulWidget {
  const PairingScreen({super.key});

  @override
  State<PairingScreen> createState() => _PairingScreenState();
}

class _PairingScreenState extends State<PairingScreen> {
  final TextEditingController _codeController = TextEditingController();
  bool _isConnected = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Device Pairing'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _isConnected ? Icons.check_circle : Icons.link,
              size: 100,
              color: _isConnected ? Colors.green : Colors.red,
            ),
            const SizedBox(height: 32),
            Text(
              _isConnected 
                ? 'Connected to Guardian Angel Device' 
                : 'Enter Device Pairing Code',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            if (!_isConnected) ...[
              TextField(
                controller: _codeController,
                decoration: const InputDecoration(
                  labelText: 'Pairing Code',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.qr_code),
                ),
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 24, letterSpacing: 4),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  if (_codeController.text.isNotEmpty) {
                    setState(() => _isConnected = true);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Device connected successfully!')),
                    );
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text('Connect Device'),
              ),
            ] else ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Text('Device Status: Online'),
                      const SizedBox(height: 8),
                      const Text('Last Check: 2 minutes ago'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          setState(() => _isConnected = false);
                          _codeController.clear();
                        },
                        child: const Text('Disconnect'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class FeedScreen extends StatelessWidget {
  const FeedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final mockAlerts = [
      {'type': 'Fall Detected', 'time': '2 minutes ago', 'status': 'Active', 'severity': 'High'},
      {'type': 'Device Offline', 'time': '1 hour ago', 'status': 'Resolved', 'severity': 'Medium'},
      {'type': 'Battery Low', 'time': '3 hours ago', 'status': 'Resolved', 'severity': 'Low'},
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Alert Feed'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: mockAlerts.length,
        itemBuilder: (context, index) {
          final alert = mockAlerts[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Icon(
                alert['type'] == 'Fall Detected' ? Icons.warning : 
                alert['type'] == 'Device Offline' ? Icons.wifi_off : Icons.battery_alert,
                color: alert['severity'] == 'High' ? Colors.red :
                       alert['severity'] == 'Medium' ? Colors.orange : Colors.yellow,
                size: 32,
              ),
              title: Text(alert['type']!),
              subtitle: Text('${alert['time']} • ${alert['status']}'),
              trailing: alert['status'] == 'Active' 
                ? ElevatedButton(
                    onPressed: () => _showAlertDetails(context, alert),
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                    child: const Text('View', style: TextStyle(color: Colors.white)),
                  )
                : null,
              onTap: () => _showAlertDetails(context, alert),
            ),
          );
        },
      ),
    );
  }

  void _showAlertDetails(BuildContext context, Map<String, String> alert) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(alert['type']!),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Time: ${alert['time']}'),
            Text('Status: ${alert['status']}'),
            Text('Severity: ${alert['severity']}'),
            const SizedBox(height: 16),
            if (alert['type'] == 'Fall Detected') ...[
              const Text('Actions taken:'),
              const Text('• Emergency contacts notified'),
              const Text('• Location shared'),
              const Text('• Video recording initiated'),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          if (alert['status'] == 'Active')
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Alert marked as resolved')),
                );
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              child: const Text('Mark Resolved', style: TextStyle(color: Colors.white)),
            ),
        ],
      ),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    child: Icon(Icons.person, size: 50),
                  ),
                  SizedBox(height: 16),
                  Text('Guardian Angel User', style: TextStyle(fontSize: 24)),
                  Text('guardian@example.com'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.notifications),
                  title: const Text('Notification Settings'),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () => _showNotificationSettings(context),
                ),
                ListTile(
                  leading: const Icon(Icons.contact_emergency),
                  title: const Text('Emergency Contacts'),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () => _showEmergencyContacts(context),
                ),
                ListTile(
                  leading: const Icon(Icons.security),
                  title: const Text('Privacy & Security'),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () {},
                ),
                ListTile(
                  leading: const Icon(Icons.help),
                  title: const Text('Help & Support'),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showNotificationSettings(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Notification Settings'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SwitchListTile(
              title: Text('Push Notifications'),
              value: true,
              onChanged: null,
            ),
            SwitchListTile(
              title: Text('SMS Alerts'),
              value: true,
              onChanged: null,
            ),
            SwitchListTile(
              title: Text('Email Alerts'),
              value: false,
              onChanged: null,
            ),
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

  void _showEmergencyContacts(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Contacts'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('1. John Doe - (555) 123-4567'),
            Text('2. Jane Smith - (555) 987-6543'),
            Text('3. Dr. Johnson - (555) 456-7890'),
            SizedBox(height: 16),
            Text('These contacts will be automatically notified in case of an emergency.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Edit'),
          ),
        ],
      ),
    );
  }
}
