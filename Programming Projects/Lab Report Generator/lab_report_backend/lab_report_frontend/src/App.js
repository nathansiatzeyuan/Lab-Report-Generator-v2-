import React, { useState, useEffect } from 'react';
import { Upload, File, Loader2 } from 'lucide-react';

// Default section options for the lab report
const defaultSectionOptions = [
  { id: 'Introduction', label: 'Introduction' },
  { id: 'Objectives', label: 'Objectives' },
  { id: 'Materials', label: 'Materials and Methods' },
  { id: 'Results', label: 'Results' },
  { id: 'Discussion', label: 'Discussion' },
  { id: 'Conclusion', label: 'Conclusion' },
  { id: 'References', label: 'References' }
];

// Alert component
const Alert = ({ children, variant }) => {
  const baseClasses = "p-4 rounded-md mb-4";
  const classes = variant === "destructive" 
    ? `${baseClasses} bg-red-50 text-red-800 border border-red-200`
    : `${baseClasses} bg-green-50 text-green-800 border border-green-200`;
  
  return <div className={classes}>{children}</div>;
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [numPages, setNumPages] = useState('');
  const [selectedSections, setSelectedSections] = useState([]);
  const [customSections, setCustomSections] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [sections, setSections] = useState([]); // Store sections from API response
  const [questions, setQuestions] = useState([]); // Store questions from API response
  const [fileInputs, setFileInputs] = useState({});
  const [textInputs, setTextInputs] = useState({});

  const handleAnswerFileChange = (key, event) => {
    // Handle the file change logic here
    const file = event.target.files[0];
    // You might want to store the file based on the key (which includes section or question id)
    console.log(key, file);  // Just for debugging purposes
  };  

  const handleAnswerTextChange = (key, event) => {
    setTextInputs({
      ...textInputs,
      [key]: event.target.value,  // Update the value for the specific section or question
    });
  };

  const handleTextChange = (id, e) => {
    const text = e.target.value;
    setTextInputs((prev) => ({ ...prev, [id]: text }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  };

  const handleSectionToggle = (sectionId) => {
    setSelectedSections(prev => 
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const handleCustomSectionsChange = (e) => {
    setCustomSections(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('number_of_pages', numPages);
    
    // Merge selected sections and custom sections
    const allSections = [...selectedSections];
    if (customSections) {
      const customSectionArray = customSections.split(',').map(section => section.trim());
      allSections.push(...customSectionArray);
    }
    
    formData.append('sections', JSON.stringify(allSections));

    try {
      const response = await fetch('http://127.0.0.1:8000/extract_text/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to process file');
      }

      // Set the sections and questions from the API response
      setSections(data.sections);
      setQuestions(data.questions);

      setSuccess('Lab report generated successfully!');
      // Reset form
      setSelectedFile(null);
      setNumPages('');
      setSelectedSections([]);
      setCustomSections('');
      setFileInputs({});
      setTextInputs({});
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6 text-gray-800">Lab Report Generator</h1>
          
          {/* First Part: File Upload and Sections */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Upload PDF</label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                <div className="space-y-1 text-center">
                  <div className="flex flex-col items-center">
                    {selectedFile ? (
                      <div className="flex items-center space-x-2">
                        <File className="h-6 w-6 text-gray-600" />
                        <span className="text-sm text-gray-600">{selectedFile.name}</span>
                      </div>
                    ) : (
                      <Upload className="h-12 w-12 text-gray-400" />
                    )}
                  </div>
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                      <span>Upload a file</span>
                      <input
                        type="file"
                        className="sr-only"
                        accept=".pdf"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">PDF up to 10MB</p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Number of Pages</label>
              <input
                type="number"
                min="1"
                value={numPages}
                onChange={(e) => setNumPages(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Select Sections</label>
              <div className="grid grid-cols-2 gap-4">
                {defaultSectionOptions.map((section) => (
                  <label key={section.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedSections.includes(section.id)}
                      onChange={() => handleSectionToggle(section.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{section.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Custom Sections (comma-separated)</label>
              <input
                type="text"
                value={customSections}
                onChange={handleCustomSectionsChange}
                placeholder="e.g. My Custom Section, Another Section"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            {error && <Alert variant="destructive">{error}</Alert>}
            {success && <Alert>{success}</Alert>}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
            >
              {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Generate Lab Report'}
            </button>
          </form>
        </div>

        {/* Second Part: Sections and Questions Display */}
        {sections.length > 0 && questions.length > 0 && (
        <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4 text-gray-800">Generated Sections and Questions</h2>
          <div className="space-y-4">
            {/* Loop through each section */}
            {sections.map((section) => (
              <div key={section.id} className="border border-gray-200 rounded-md p-4 mb-4">
                <h4 className="text-md font-medium">{section.section}</h4> {/* Display section.text */}
                <div className="flex flex-col space-y-4">
                  {/* Answer Text Input for section */}
                  <input
                    type="text"
                    value={textInputs[`section-${section.id}-text`] || ''} // Use section.id as part of the key
                    onChange={(e) => handleAnswerTextChange(`section-${section.id}-text`, e)} // Handle changes based on section.id
                    placeholder="Your answer here..."
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                  />

                  {/* File Upload Input for section */}
                  <input
                    type="file"
                    onChange={(e) => handleAnswerFileChange(`section-${section.id}-file`, e)} // Use section.id to identify file change
                    className="mt-1 block w-full text-sm text-gray-500"
                  />
                </div>
              </div>
            ))}

            {/* Loop through each question */}
            {questions.map((question) => (
              <div key={question.id} className="border border-gray-200 rounded-md p-4 mb-4">
                <h4 className="text-md font-medium">{question.question_text}</h4> {/* Display question.text */}
                <div className="flex flex-col space-y-4">
                  {/* Answer Text Input for question */}
                  <input
                    type="text"
                    value={textInputs[`question-${question.id}-text`] || ''} // Use question.id as part of the key
                    onChange={(e) => handleAnswerTextChange(`question-${question.id}-text`, e)} // Handle changes based on question.id
                    placeholder="Your answer here..."
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                  />

                  {/* File Upload Input for question */}
                  <input
                    type="file"
                    onChange={(e) => handleAnswerFileChange(`question-${question.id}-file`, e)} // Use question.id to identify file change
                    className="mt-1 block w-full text-sm text-gray-500"
                  />
                </div>
              </div>
            ))}
          </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
