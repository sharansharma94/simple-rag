import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';

const API_URL = 'http://localhost:8000';

interface QueryInterfaceProps {
  onQueryResult?: (answer: string, context: string) => void;
}

export function QueryInterface({ onQueryResult }: QueryInterfaceProps) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setIsLoading(true);
    setAnswer('');
    
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 3
        }),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnswer(data.answer);
      
      // Pass the result to parent component
      if (onQueryResult) {
        onQueryResult(data.answer, data.context);
      }
    } catch (error) {
      console.error('Query error:', error);
      toast.error(`Query failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle>Ask a Question</CardTitle>
          <CardDescription>
            Enter your question to query the knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Textarea
              placeholder="Enter your question here..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-h-24"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !query.trim()}
              className="w-full sm:w-auto self-end"
            >
              {isLoading ? 'Querying...' : 'Submit Query'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {answer && (
        <Card className="w-full h-full">
          <CardHeader className="pb-3">
            <CardTitle>Answer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap p-4 bg-muted rounded-md h-full overflow-auto">
              {answer}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
