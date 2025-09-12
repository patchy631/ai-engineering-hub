interface SectionTitleProps {
  title: string
}

export function SectionTitle({ title }: SectionTitleProps) {
  return (
    <div className="border-b border-[#D8D8E5] pb-1">
      <h2 className="text-lg font-semibold text-[#030507] font-['Roobert']">{title}</h2>
    </div>
  )
}
