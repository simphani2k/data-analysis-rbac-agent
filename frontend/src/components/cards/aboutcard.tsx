import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function AboutCard() {
  return (
    <div className="max-w-3xl mx-auto mt-20 px-4">
      <Card className="border-2 shadow-lg">
        <CardHeader className="text-center pb-4">
          <CardTitle className="text-3xl font-bold">Data Analysis AI Agent</CardTitle>
          <CardDescription className="text-base mt-2">
            AI-powered data analysis with role-based access control
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground leading-relaxed space-y-4">
          <p>
            Welcome to your intelligent data analysis assistant. Ask questions about your retail data,
            get insights, and explore patterns using natural language.
          </p>
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <p className="font-semibold text-gray-900">Key Features:</p>
            <ul className="space-y-1 ml-4">
              <li>• Natural language data queries</li>
              <li>• Real-time streaming responses</li>
              <li>• Multi-table retail data analysis</li>
              <li>• Powered by advanced AI models</li>
            </ul>
          </div>
          <p className="text-center text-xs text-gray-500 pt-2">
            Start a conversation by typing your question below
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
