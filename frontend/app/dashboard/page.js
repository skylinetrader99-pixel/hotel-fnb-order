"use client";

import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [orders, setOrders] = useState([]);

  async function fetchOrders() {
    const res = await fetch("http://127.0.0.1:8000/orders", {
      cache: "no-store",
    });

    const data = await res.json();
    setOrders(data);
  }

  async function updateStatus(orderId, status) {
    await fetch(`http://127.0.0.1:8000/orders/${orderId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });

    fetchOrders();
  }

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  function getColor(status) {
    switch (status) {
      case "new":
        return "bg-blue-100";
      case "preparing":
        return "bg-yellow-100";
      case "ready":
        return "bg-purple-100";
      case "delivered":
        return "bg-green-100";
      default:
        return "bg-gray-100";
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <h1 className="mb-6 text-2xl font-bold">Kitchen Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {orders.map((order) => (
          <div
            key={order.order_id}
            className={`rounded-2xl p-4 shadow ${getColor(order.status)}`}
          >
            <p className="font-bold">Order #{order.order_id}</p>
            <p>Room: {order.room_number}</p>
            <p>Status: {order.status}</p>

            <div className="mt-3 space-y-1 text-sm">
              {order.items.map((item, i) => (
                <div key={i}>
                  {item.name_th} x {item.qty}
                </div>
              ))}
            </div>

            <div className="mt-4 flex gap-2 flex-wrap">
              <button
                onClick={() => updateStatus(order.order_id, "preparing")}
                className="rounded bg-yellow-500 px-2 py-1 text-white"
              >
                Preparing
              </button>

              <button
                onClick={() => updateStatus(order.order_id, "ready")}
                className="rounded bg-purple-500 px-2 py-1 text-white"
              >
                Ready
              </button>

              <button
                onClick={() => updateStatus(order.order_id, "delivered")}
                className="rounded bg-green-600 px-2 py-1 text-white"
              >
                Delivered
              </button>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}