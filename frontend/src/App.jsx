import React from "react";
import { Toaster } from "react-hot-toast";
import Sidebar from "./components/sidebar/Sidebar";
import ChatWindow from "./components/chat/ChatWindow";
import { useIngest } from "./hooks/useIngest";

function App() {
  const {
    sites, activeSiteId, ingestStatus, isIngesting,
    ingestUrl, selectSite, removeSite,
  } = useIngest();

  const activeSite = sites.find((s) => s.site_id === activeSiteId);

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#18181b",
            color: "#f4f4f5",
            border: "1px solid #3f3f46",
            fontSize: "13px",
          },
        }}
      />

      <Sidebar
        sites={sites}
        activeSiteId={activeSiteId}
        ingestStatus={ingestStatus}
        isIngesting={isIngesting}
        onIngest={ingestUrl}
        onSelectSite={selectSite}
        onRemoveSite={removeSite}
      />

      <main className="flex-1 min-w-0 flex flex-col">
        <ChatWindow
          siteId={activeSiteId}
          siteTitle={activeSite?.title || activeSite?.url}
        />
      </main>
    </div>
  );
}

export default App;
