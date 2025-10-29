import { JSXElementConstructor } from "react";
import Image from "next/image";

export const SourceIcon = ({ id }: { id: string }) => {
  return (
    <div className="relative">
      <div className="">
        {id && (
          <Image
            alt={id}
            width={36}
            height={36}
            className="h-10 w-10 aspect-square"
            src={`/icons/${id}.svg`}
          />
        )}
      </div>
    </div>
  );
};
