import { motion } from "framer-motion";
import { cn } from "../lib/utils";

const typeColors = {
  llm_call: "bg-[#4da6ff] border-[#4da6ff]",
  tool_call: "bg-[#8b8d91] border-[#8b8d91]",
  agent_step: "bg-accent border-accent",
  error: "bg-[#ff5b5b] border-[#ff5b5b]",
};

export function Timeline({ steps, selectedStepId, onSelectStep }) {
  if (!steps || steps.length === 0) return null;

  const every = steps.length > 60 ? Math.ceil(steps.length / 60) : 1;
  const visible = steps.filter((_, i) => i % every === 0).slice(0, 60);

  return (
    <div className="p-4 px-8">
      <div className="flex justify-between items-center mb-3">
        <div className="text-[11px] font-bold text-muted uppercase tracking-wider">Timeline</div>
        <div className="text-xs text-[#8b8d91]">{visible.length} visible · {steps.length} total</div>
      </div>
      
      <div className="flex items-center py-2 overflow-x-auto no-scrollbar scroll-smooth">
        {visible.map((step, idx) => {
          const isActive = String(step.step_id) === String(selectedStepId);
          const isError = !!step.error;
          const typeClass = isError ? typeColors.error : (typeColors[step.type] || "bg-[#3e3e3e] border-[#3e3e3e]");
          
          return (
            <button
              key={step.step_id}
              onClick={() => onSelectStep(step.step_id)}
              className="relative flex items-center flex-none group outline-none"
              title={step.name || step.type || "step"}
            >
              <div className="relative flex flex-col items-center">
                <motion.div
                  initial={false}
                  animate={{
                    scale: isActive ? 1.2 : 1,
                  }}
                  className={cn(
                    "w-3.5 h-3.5 rounded-full border-2 transition-colors",
                    typeClass,
                    isActive ? "ring-2 ring-offset-2 ring-offset-[#1E1E1E] ring-accent" : ""
                  )}
                />
                <span className={cn(
                  "absolute top-5 text-[10px] font-mono whitespace-nowrap transition-colors",
                  isActive ? "text-[#ededed] font-bold" : "text-muted group-hover:text-[#c2c2c2]"
                )}>
                  {step.step_id}
                </span>
              </div>
              
              {idx < visible.length - 1 && (
                <div className="w-8 h-[1px] mx-1 rounded-full relative bg-[#3e3e3e]" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
