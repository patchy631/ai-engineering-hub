/* eslint-disable react/jsx-no-comment-textnodes */
import { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

function Badge({ ...attrs }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...attrs}
      className={cn(
        attrs.className,
        "flex gap-10 bg-background-base relative w-max pb-16 items-center text-label-x-small",
      )}
    >
      <div className="h-1 bottom-0 absolute w-full left-0 bg-border-faint" />
      <div className="text-black-alpha-16 pointer-events-none select-none">
        //
      </div>
      <div className="relative flex gap-10 items-center">{attrs.children}</div>
      <div className="text-black-alpha-16 pointer-events-none select-none -scale-x-100">
        //
      </div>
    </div>
  );
}

export default Badge;
export { Badge };
