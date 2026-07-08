import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api, streamChat } from "../api/client";
import BackBar from "../components/BackBar";
import Spinner from "../components/Spinner";
import QuizModal from "../components/QuizModal";

export default function ChatPage() {
  const { subjectId } = useParams();
  const { t } = useTranslation();

  const [blocked, setBlocked] = useState(null); // null=checking, false/obj
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [quizOpen, setQuizOpen] = useState(false);
  const bottomRef = useRef(null);

  const loadConversations = () =>
    api.get("/chat/conversations").then(setConversations).catch(() => {});

  useEffect(() => {
    api
      .get(`/restrictions/check/${subjectId}`)
      .then((r) => setBlocked(r.blocked ? r : false))
      .catch(() => setBlocked(false));
    loadConversations();
  }, [subjectId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const openConversation = async (id) => {
    const conv = await api.get(`/chat/conversations/${id}`);
    setConversationId(conv.id);
    setMessages(
      conv.messages.map((m) => ({ role: m.role, content: m.content, sources: m.sources }))
    );
  };

  const newChat = () => {
    setConversationId(null);
    setMessages([]);
  };

  const send = async (e) => {
    e?.preventDefault();
    const question = input.trim();
    if (!question || streaming) return;

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", sources: [], streaming: true },
    ]);
    setInput("");
    setStreaming(true);

    await streamChat(
      {
        subject_id: Number(subjectId),
        question,
        conversation_id: conversationId,
        history,
      },
      {
        onMeta: (data) => {
          setConversationId(data.conversation_id);
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1].sources = data.sources || [];
            return copy;
          });
        },
        onToken: (text) => {
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1].content += text;
            return copy;
          });
        },
        onError: (err) => {
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1].content =
              (copy[copy.length - 1].content || "") + `\n⚠️ ${err.message}`;
            copy[copy.length - 1].streaming = false;
            return copy;
          });
        },
        onDone: () => {
          setMessages((prev) => {
            const copy = [...prev];
            if (copy.length) copy[copy.length - 1].streaming = false;
            return copy;
          });
          setStreaming(false);
          loadConversations();
        },
      }
    );
  };

  if (blocked === null) return <Spinner label={t("common.loading")} />;

  if (blocked) {
    return (
      <>
        <BackBar />
        <div className="card mx-auto max-w-lg text-center">
          <div className="mb-3 text-4xl">🔒</div>
          <h2 className="text-xl font-bold">{t("chat.blocked")}</h2>
          {blocked.reason && <p className="mt-2 text-slate-500">{blocked.reason}</p>}
        </div>
      </>
    );
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
      {/* Sidebar */}
      <aside className="hidden lg:block">
        <BackBar />
        <button className="btn-primary mb-3 w-full" onClick={newChat}>
          ＋ {t("chat.newChat")}
        </button>
        <div className="mb-2 text-sm font-semibold text-slate-500">
          {t("chat.conversations")}
        </div>
        <div className="space-y-1">
          {conversations.length === 0 && (
            <p className="text-sm text-slate-400">{t("chat.noConversations")}</p>
          )}
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => openConversation(c.id)}
              className={`block w-full truncate rounded-lg px-3 py-2 text-start text-sm hover:bg-slate-100 dark:hover:bg-slate-700 ${
                c.id === conversationId ? "bg-slate-100 dark:bg-slate-700" : ""
              }`}
            >
              {c.title}
            </button>
          ))}
        </div>
      </aside>

      {/* Chat area */}
      <section className="flex h-[calc(100vh-8rem)] flex-col rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <span className="font-semibold">{t("nav.chat")}</span>
          <button className="btn-ghost" onClick={() => setQuizOpen(true)}>
            📝 {t("chat.quiz")}
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="grid h-full place-items-center text-center text-slate-400">
              <div>
                <div className="mb-2 text-4xl">💬</div>
                {t("chat.placeholder")}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} />
          ))}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={send}
          className="flex items-end gap-2 border-t border-slate-200 p-3 dark:border-slate-700"
        >
          <textarea
            className="input max-h-40 min-h-[44px] flex-1 resize-none"
            rows={1}
            placeholder={t("chat.placeholder")}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) send(e);
            }}
          />
          <button className="btn-primary" disabled={streaming || !input.trim()}>
            {streaming ? t("chat.thinking") : t("chat.send")}
          </button>
        </form>
      </section>

      {quizOpen && (
        <QuizModal subjectId={Number(subjectId)} onClose={() => setQuizOpen(false)} />
      )}
    </div>
  );
}

function MessageBubble({ message }) {
  const { t } = useTranslation();
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-brand-600 text-white"
            : "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-100"
        }`}
      >
        <div className="whitespace-pre-wrap leading-relaxed">
          {message.content || (message.streaming ? "…" : "")}
        </div>
        {!isUser && message.sources?.length > 0 && (
          <details className="mt-2 text-xs opacity-80">
            <summary className="cursor-pointer">📖 {message.sources.length}</summary>
            <ul className="mt-1 space-y-1">
              {message.sources.map((s, i) => (
                <li key={i} className="border-s-2 border-brand-400 ps-2">
                  {s.source}
                  {s.page ? ` · p.${s.page}` : ""}
                </li>
              ))}
            </ul>
          </details>
        )}
        {!isUser && message.content && !message.streaming && (
          <button
            className="mt-2 text-xs opacity-70 hover:opacity-100"
            onClick={() => navigator.clipboard.writeText(message.content)}
          >
            {t("chat.copy")}
          </button>
        )}
      </div>
    </div>
  );
}
