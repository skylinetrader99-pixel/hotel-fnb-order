"use client";

import { use, useEffect, useState } from "react";

export default function OrderStatusPage({ params }) {
  const { order_id } = use(params);

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let intervalId;

    async function loadOrder() {
      try {
        const res = await fetch(`http://127.0.0.1:8000/orders/${order_id}`, {
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error("Failed to fetch order");
        }

        const data = await res.json();
        setOrder(data);
        setError("");
      } catch (err) {
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    }

    loadOrder();
    intervalId = setInterval(loadOrder, 5000);

    return () => clearInterval(intervalId);
  }, [order_id]);

  if (loading) {
    return <main className="p-6">Loading order...</main>;
  }

  if (error) {
    return <main className="p-6 text-red-600">Error: {error}</main>;
  }

  function getStatusColor(status) {
    switch (status) {
      case "new":
        return "bg-blue-100 text-blue-800";
      case "accepted":
        return "bg-indigo-100 text-indigo-800";
      case "preparing":
        return "bg-yellow-100 text-yellow-800";
      case "ready":
        return "bg-purple-100 text-purple-800";
      case "delivered":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-6 shadow">
        <h1 className="text-2xl font-bold text-gray-900">Order Status</h1>

        <div className="mt-4 space-y-2 text-gray-700">
          <p><strong>Order ID:</strong> {order.order_id}</p>
          <p><strong>Room:</strong> {order.room_number}</p>
          <p>
            <strong>Status:</strong>{" "}
            <span className={`rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(order.status)}`}>
              {order.status}
            </span>
          </p>
          <p><strong>Total:</strong> ฿{order.total_amount}</p>
          <p><strong>Created:</strong> {order.created_at}</p>
        </div>

        <div className="mt-6">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Items</h2>
          <div className="space-y-3">
            {order.items.map((item, index) => (
              <div key={index} className="rounded-xl bg-gray-50 p-3">
                <p className="font-medium text-gray-900">{item.name_th}</p>
                <p className="text-sm text-gray-600">
                  Qty: {item.qty} | Unit: ฿{item.unit_price} | Total: ฿{item.line_total}
                </p>
              </div>
            ))}
          </div>
        </div>

        <p className="mt-6 text-sm text-gray-500">
          Status refreshes automatically every 5 seconds.
        </p>
      </div>
    </main>
  );
}