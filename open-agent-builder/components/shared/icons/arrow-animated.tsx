import { cx } from "class-variance-authority";

export function ArrowAnimated({
  className,
  ...props
}: React.HTMLAttributes<SVGElement>) {
  return (
    <svg
      className={cx("-mr-1 ml-1.5 stroke-[1.5px]", className)}
      fill="none"
      stroke="currentColor"
      width="11"
      height="11"
      viewBox="0 0 10 10"
      aria-hidden="true"
      {...props}
    >
      <path
        className="opacity-0 transition group-hover:opacity-100"
        d="M0 5h7"
      />
      <path
        className="transition group-hover:translate-x-[3px]"
        d="M1 1l4 4-4 4"
      />
    </svg>
  );
}
