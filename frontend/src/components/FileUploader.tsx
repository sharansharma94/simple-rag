import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { toast } from 'sonner';

const API_URL = 'http://localhost:8000';

export function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      toast.success(data.message || 'File uploaded successfully');
      setFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="w-full sticky top-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Upload Document</CardTitle>
        <CardDescription className="text-xs">
          Add documents to the knowledge base
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-3">
          <div className="grid w-full items-center gap-1.5">
            <input
              id="document"
              type="file"
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              onChange={handleFileChange}
              accept=".txt,.pdf,.doc,.docx"
              disabled={isUploading}
            />
            {file && (
              <p className="text-xs text-muted-foreground truncate">
                Selected: {file.name}
              </p>
            )}
          </div>
          <Button 
            onClick={handleUpload} 
            disabled={!file || isUploading}
            className="w-full"
            size="sm"
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
