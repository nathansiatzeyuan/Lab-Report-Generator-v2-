import 'package:flutter/material.dart';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:convert';

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
  // State variables for user inputs
  File? _labReportFile;
  int? _pageLimit;
  List<String> _selectedSections = [];
  File? _imageFile;

  // List of sections
  final List<String> sections = ['Introduction', 'Methods', 'Results'];

  // Method to pick lab report PDF file
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

  // Method to pick image file
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

  // Method to handle form submission (send data to the backend)
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

        if (response.statusCode == 200) {
          var responseData = await response.stream.bytesToString();
          print('Success! Response: $responseData');
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Button to upload lab report
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

            // Input for page limit
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

            // Dropdown to select sections
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

            // Button to upload image
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

            // Generate button to submit data
            Center(
              child: ElevatedButton(
                onPressed: _submitData,
                child: const Text('Generate Lab Report'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
