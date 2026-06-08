import { useState, useCallback, useEffect, useRef } from "react";
import { startIngest, createProgressStream, listSites, deleteSite } from "../services/api";
import toast from "react-hot-toast";

export const useIngest = () => {
  const [sites, setSites] = useState([]);
  const [activeSiteId, setActiveSiteId] = useState(null);
  const [ingestStatus, setIngestStatus] = useState(null); // { status, pages_crawled, chunks_count, title }
  const [isIngesting, setIsIngesting] = useState(false);
  const eventSourceRef = useRef(null);

  const loadSites = useCallback(async () => {
    try {
      const data = await listSites();
      setSites(data.filter((s) => s.status === "ready"));
    } catch (_) {}
  }, []);

  useEffect(() => {
    loadSites();
  }, [loadSites]);

  const _closeStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const ingestUrl = useCallback(
    async (url) => {
      if (isIngesting) return;
      setIsIngesting(true);
      setIngestStatus({ status: "starting", pages_crawled: 0, chunks_count: 0, title: url });

      try {
        const { site_id } = await startIngest(url);
        setActiveSiteId(site_id);

        _closeStream();
        const es = createProgressStream(site_id);
        eventSourceRef.current = es;

        es.onmessage = (e) => {
          const data = JSON.parse(e.data);
          setIngestStatus(data);

          if (data.status === "ready") {
            toast.success(`✅ "${data.title}" indexed successfully!`);
            setIsIngesting(false);
            _closeStream();
            loadSites();
          } else if (data.status === "error") {
            toast.error("Ingestion failed. Please try again.");
            setIsIngesting(false);
            _closeStream();
          }
        };

        es.onerror = () => {
          toast.error("Connection lost during ingestion.");
          setIsIngesting(false);
          _closeStream();
        };
      } catch (err) {
        toast.error(err?.response?.data?.detail || "Failed to start ingestion.");
        setIsIngesting(false);
      }
    },
    [isIngesting, _closeStream, loadSites]
  );

  const selectSite = useCallback((siteId) => {
    setActiveSiteId(siteId);
  }, []);

  const removeSite = useCallback(
    async (siteId) => {
      try {
        await deleteSite(siteId);
        setSites((prev) => prev.filter((s) => s.site_id !== siteId));
        if (activeSiteId === siteId) setActiveSiteId(null);
        toast.success("Site removed.");
      } catch (_) {
        toast.error("Failed to remove site.");
      }
    },
    [activeSiteId]
  );

  return {
    sites,
    activeSiteId,
    ingestStatus,
    isIngesting,
    ingestUrl,
    selectSite,
    removeSite,
  };
};
