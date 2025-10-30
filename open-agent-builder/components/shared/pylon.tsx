"use client";

import { useEffect } from "react";
import Script from "next/script";

const pylon_app_id = "da167302-89d0-41fa-b794-0f8d19c70b68";

interface PylonChatProps {
  user: {
    email?: string | undefined;
  };
  nonce: string;
}

const PylonChat: React.FC<PylonChatProps> = ({ user, nonce }) => {
  useEffect(() => {
    // If there's no user.email, do nothing.
    if (!user?.email) return;

    // Mount/initialize Pylon
    (window as any).pylon = {
      chat_settings: {
        app_id: pylon_app_id,
        email: user.email,
        name: user.email,
      },
    };

    // The cleanup function to run when the user logs out
    // or when this component unmounts.
    return () => {
      try {
        console.log("Unmounting Pylon script...");

        // If Pylon provides a remove/destroy function, call it:
        if (
          (window as any).Pylon &&
          typeof (window as any).Pylon.remove === "function"
        ) {
          (window as any).Pylon.remove();
        }

        // Remove the script tag from the DOM, if you wish:
        const pylonScript = document.getElementById("pylon-script");
        if (pylonScript) {
          pylonScript.remove();
        }

        // Also remove the global Pylon variables, if desired:
        delete (window as any).Pylon;
        delete (window as any).pylon;
      } catch (error) {
        console.error("Error unmounting Pylon script:", error);
      }
    };
  }, [user]);

  // Only render the script if we have a user email
  if (!user?.email) {
    console.log("No user email found, not rendering Pylon chat");
    return null;
  }

  return (
    <Script
      id="pylon-script"
      nonce={nonce}
      strategy="afterInteractive"
      onLoad={() => {}}
      onError={(e) => {
        console.error("Error loading Pylon script:", e);
      }}
      dangerouslySetInnerHTML={{
        __html: `
          (function(){
            var e=window;
            var t=document;
            var n=function(){n.e(arguments)};
            n.q=[];
            n.e=function(e){n.q.push(e)};
            e.Pylon=n;
            var r=function(){
              var s=t.createElement("script");
              s.setAttribute("type","text/javascript");
              s.setAttribute("async","true");
              s.setAttribute("src","https://widget.usepylon.com/widget/${pylon_app_id}");
              var o=t.getElementsByTagName("script")[0];
              o.parentNode.insertBefore(s,o)
            };
            if(t.readyState==="complete"){ 
              r()
            } else if(e.addEventListener){
              e.addEventListener("load",r,false)
            }
          })();
        `,
      }}
    />
  );
};

export default PylonChat;
