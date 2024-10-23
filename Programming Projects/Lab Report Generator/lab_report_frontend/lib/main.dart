import 'package:flutter/material.dart';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:convert';
import 'package:flutter/services.dart'; // Import for Clipboard functionality

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lab Report Generator',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Lab Report Generator'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  File? _labReportFile;
  int? _pageLimit;
  List<String> _selectedSections = [];
  File? _imageFile;
  String _responseData = '';  // New variable to store the response data

  final List<String> sections = ['Introduction', 'Methods', 'Results'];

  Future<void> _pickLabReport() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );

    if (result != null) {
      setState(() {
        _labReportFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> _pickImage() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.image,
    );

    if (result != null) {
      setState(() {
        _imageFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> _submitData() async {
    if (_labReportFile != null && _pageLimit != null && _selectedSections.isNotEmpty) {
      try {
        var uri = Uri.parse('http://127.0.0.1:8000/generate/');  // Replace with your backend API URL
        var request = http.MultipartRequest('POST', uri);

        // Add file fields
        request.files.add(await http.MultipartFile.fromPath(
          'pdf',
          _labReportFile!.path,
          contentType: MediaType('application', 'pdf'),
        ));

        if (_imageFile != null) {
          request.files.add(await http.MultipartFile.fromPath(
            'image',
            _imageFile!.path,
            contentType: MediaType('image', 'jpeg'),  // Adjust based on the image type
          ));
        }

        // Add other form fields
        request.fields['page_limit'] = _pageLimit.toString();
        request.fields['sections_needed'] = jsonEncode(_selectedSections);

        // Send the request to the server
        var response = await request.send();

        // Read the response once
        if (response.statusCode == 200) {
          var responseData = await response.stream.bytesToString();
          setState(() {
            _responseData = jsonDecode(responseData)["lab_report"]; // Store response data
          });
        } else {
          print('Failed to submit data. Status code: ${response.statusCode}');
        }
      } catch (e) {
        print('Error submitting data: $e');
      }
    } else {
      print("Please fill in all the required fields.");
    }
  }

  void _copyToClipboard() {
    Clipboard.setData(ClipboardData(text: _responseData)).then((_) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report copied to clipboard!')),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lab Report Generator'),
      ),
      body: SingleChildScrollView( // Use SingleChildScrollView for the whole body
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton(
              onPressed: _pickLabReport,
              child: const Text('Upload Lab Report (PDF)'),
            ),
            if (_labReportFile != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Text('Selected file: ${_labReportFile!.path}'),
              ),
            const SizedBox(height: 16),

            TextField(
              decoration: const InputDecoration(
                labelText: 'Specify Page Limit',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              onChanged: (value) {
                setState(() {
                  _pageLimit = int.tryParse(value);
                });
              },
            ),
            const SizedBox(height: 16),

            const Text('Select Sections Needed:'),
            Wrap(
              spacing: 8.0,
              children: sections.map((section) {
                return ChoiceChip(
                  label: Text(section),
                  selected: _selectedSections.contains(section),
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedSections.add(section);
                      } else {
                        _selectedSections.remove(section);
                      }
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            ElevatedButton(
              onPressed: _pickImage,
              child: const Text('Upload Image (Readings/Values)'),
            ),
            if (_imageFile != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Text('Selected image: ${_imageFile!.path}'),
              ),
            const SizedBox(height: 16),

            Center(
              child: ElevatedButton(
                onPressed: _submitData,
                child: const Text('Generate Lab Report'),
              ),
            ),
            const SizedBox(height: 16),
           // Display the generated report if available
            if (_responseData.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Generated Lab Report:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                constraints: const BoxConstraints(
                  maxHeight: 300, // Set a maximum height for the container
                ),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey), // Optional: Add a border for visibility
                  borderRadius: BorderRadius.circular(8), // Optional: Rounded corners
                ),
                child: SingleChildScrollView(
                  scrollDirection: Axis.vertical,
                  child: Text(
                    _responseData,
                    style: const TextStyle(fontFamily: 'Courier', fontSize: 14),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: _copyToClipboard,
                child: const Text('Copy Text'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
