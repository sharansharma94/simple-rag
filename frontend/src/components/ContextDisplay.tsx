import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface ContextDisplayProps {
  context: string;
}

export function ContextDisplay({ context }: ContextDisplayProps) {
  if (!context) return null;
  
  return (
    <Card className="w-full mt-6">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Context Used</CardTitle>
        <CardDescription className="text-xs">
          Retrieved documents used for the answer
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="whitespace-pre-wrap p-3 bg-muted rounded-md text-sm max-h-[500px] overflow-auto">
          {context}
        </div>
      </CardContent>
    </Card>
  );
}
