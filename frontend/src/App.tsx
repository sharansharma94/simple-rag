import './App.css'
import { Toaster } from 'sonner'
import { useState } from 'react'
import { FileUploader } from './components/FileUploader'
import { QueryInterface } from './components/QueryInterface'
import { ContextDisplay } from './components/ContextDisplay'

function App() {
  const [, setAnswer] = useState('')
  const [context, setContext] = useState('')

  const handleQueryResult = (newAnswer: string, newContext: string) => {
    setAnswer(newAnswer)
    setContext(newContext)
  }

  return (
    <div className='flex flex-col min-h-screen p-4 max-w-7xl mx-auto'>
      <Toaster position="top-right" richColors />
      
      <header className='mb-6'>
        <h1 className='text-3xl font-bold text-center'>RAG Application</h1>
        <p className='text-center text-muted-foreground mt-2'>
          Upload documents and ask questions using Retrieval-Augmented Generation
        </p>
      </header>
      
      <main className='flex-grow flex flex-col md:flex-row gap-6'>
        <div className='flex-grow order-2 md:order-1'>
          <QueryInterface onQueryResult={handleQueryResult} />
        </div>
        
        <div className='md:w-80 shrink-0 order-1 md:order-2 flex flex-col'>
          <FileUploader />
          <ContextDisplay context={context} />
        </div>
      </main>
      
      <footer className='mt-auto py-4 text-center text-sm text-muted-foreground border-t mt-8'>
        Simple RAG Application with Qdrant and Ollama
      </footer>
    </div>
  )
}

export default App
