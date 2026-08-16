export function Kpi({ label, value, trend, tone = "default", testId }) {
  const toneMap = {
    default: "text-white",
    violet: "text-violet-300",
    gold: "text-amber-400",
    green: "text-emerald-400",
    red: "text-red-400",
  };
  return (
    <div data-testid={testId} className="surface-card p-4 relative">
      <div className="label-cap">{label}</div>
      <div className={`kpi-value text-2xl md:text-3xl mt-2 tabular-nums ${toneMap[tone]}`}>
        {value}
      </div>
      {trend && (
        <div className="label-cap mt-1 text-emerald-400">
          {trend}
        </div>
      )}
    </div>
  );
}

export function CardShell({ title, right, testId, children, className = "" }) {
  return (
    <div data-testid={testId} className={`surface-card p-5 ${className}`}>
      {(title || right) && (
        <div className="flex items-center justify-between mb-4">
          {title && <div className="label-cap">{title}</div>}
          {right}
        </div>
      )}
      {children}
    </div>
  );
}

export function StatusDot({ health }) {
  const map = { green: "dot-green", amber: "dot-amber", red: "dot-red", info: "dot-blue" };
  return <span className={`dot-status ${map[health] || "dot-blue"}`} />;
}

export function SeverityBadge({ severity }) {
  const map = {
    critical: "bg-red-500/15 text-red-400 border-red-500/40",
    warning: "bg-amber-500/15 text-amber-400 border-amber-500/40",
    info: "bg-blue-500/15 text-blue-400 border-blue-500/40",
    high: "bg-red-500/15 text-red-400 border-red-500/40",
    medium: "bg-amber-500/15 text-amber-400 border-amber-500/40",
    low: "bg-blue-500/15 text-blue-400 border-blue-500/40",
  };
  return (
    <span
      className={`inline-block px-1.5 py-0.5 rounded-sm border text-[10px] font-mono uppercase tracking-widest ${
        map[severity] || map.info
      }`}
    >
      {severity}
    </span>
  );
}
