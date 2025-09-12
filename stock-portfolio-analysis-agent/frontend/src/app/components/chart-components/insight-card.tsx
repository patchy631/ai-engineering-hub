interface Insight {
  title: string
  description: string
  emoji: string
}

interface InsightCardComponentProps {
  insight: Insight
  type: "bull" | "bear"
}

export function InsightCardComponent({ insight, type }: InsightCardComponentProps) {
  const getTypeStyles = () => {
    switch (type) {
      case "bull":
        return "border-l-4 border-l-[#00d237] bg-[#86ECE4]/10"
      case "bear":
        return "border-l-4 border-l-red-500 bg-red-50"
      default:
        return "border-l-4 border-l-[#D8D8E5]"
    }
  }

  return (
    <div className={`bg-white border border-[#D8D8E5] rounded-xl p-3 ${getTypeStyles()}`}>
      <div className="flex items-start gap-2">
        <span className="text-lg">{insight.emoji}</span>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-[#030507] font-['Roobert'] mb-1">{insight.title}</h3>
          <p className="text-xs text-[#575758] font-['Plus_Jakarta_Sans'] leading-relaxed">{insight.description}</p>
        </div>
      </div>
    </div>
  )
}
