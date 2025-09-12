export interface Allocation {
  ticker: string
  allocation: number
  currentValue: number
  totalReturn: number
}

interface AllocationTableComponentProps {
  allocations: Allocation[] | [] | undefined
  size?: "normal" | "small"
}

export function AllocationTableComponent({ allocations, size = "normal" }: AllocationTableComponentProps) {
  // Define class variants based on size
  const padding = size === "small" ? "py-1 px-2" : "py-2 px-3"
  const fontSize = size === "small" ? "text-[10px]" : "text-xs"
  return (
    <div className="bg-white border border-[#D8D8E5] rounded-xl overflow-hidden">
      <table className="w-full">
        <thead className="bg-[#FAFCFA]">
          <tr>
            <th className={`text-left ${padding} ${fontSize} font-semibold text-[#030507] font-['Plus_Jakarta_Sans']`}>
              Ticker
            </th>
            <th className={`text-left ${padding} ${fontSize} font-semibold text-[#030507] font-['Plus_Jakarta_Sans']`}>%</th>
            <th className={`text-left ${padding} ${fontSize} font-semibold text-[#030507] font-['Plus_Jakarta_Sans']`}>
              Value
            </th>
            <th className={`text-left ${padding} ${fontSize} font-semibold text-[#030507] font-['Plus_Jakarta_Sans']`}>
              Return
            </th>
          </tr>
        </thead>
        <tbody>
          {allocations?.map((allocation, index) => (
            <tr key={allocation.ticker} className={index % 2 === 0 ? "bg-white" : "bg-[#FAFCFA]"}>
              <td className={`font-medium text-[#030507] font-['Plus_Jakarta_Sans'] ${padding} ${fontSize}`}>
                {allocation.ticker}
              </td>
              <td className={`text-[#575758] font-['Plus_Jakarta_Sans'] ${padding} ${fontSize}`}>{allocation.allocation.toFixed(2)}%</td>
              <td className={`text-[#575758] font-['Plus_Jakarta_Sans'] ${padding} ${fontSize}`}>
                ${(allocation.currentValue / 1000).toFixed(1)}K
              </td>
              <td className={`font-medium font-['Plus_Jakarta_Sans'] ${padding} ${fontSize}`}>
                <span className={allocation.totalReturn >= 0 ? "text-[#1B606F]" : "text-red-600"}>
                  {allocation.totalReturn >= 0 ? "+" : ""}
                  {allocation.totalReturn.toFixed(1)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
