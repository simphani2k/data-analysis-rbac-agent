import { checkAIAvailability } from "@/app/actions";

export default async function EnvCard() {
  const result = await checkAIAvailability();
  return !result && (
    <div className="absolute inset-0 top-10 left-0 right-0 flex items-center justify-center w-md">
      <div className="bg-red-500 text-slate-50 rounded shadow-md p-2 leading-tight">
        <h2 className="text-sm font-bold">⚠️ AI Orchestrator Unavailable</h2>
        <p className="text-xs flex flex-col gap-1 mt-1">
          <span>Cannot connect to the AI Orchestrator backend.</span>
          <span className="font-semibold">Possible causes:</span>
          <span>• GROQ_API_URL not set in Vercel environment variables</span>
          <span>• Backend server is not running or not publicly accessible</span>
          <span>• EC2 security group blocking Vercel&apos;s IP ranges</span>
        </p>
      </div>
    </div>
  );
}
