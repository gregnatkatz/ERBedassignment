use actix_web::{web, HttpRequest, HttpResponse, Result};
use actix_ws::Message;

pub async fn ws_index(req: HttpRequest, stream: web::Payload) -> Result<HttpResponse> {
    let (response, mut session, mut msg_stream) = actix_ws::handle(&req, stream)?;
    
    actix_web::rt::spawn(async move {
        while let Some(Ok(msg)) = msg_stream.recv().await {
            match msg {
                Message::Ping(bytes) => {
                    if session.pong(&bytes).await.is_err() {
                        return;
                    }
                }
                Message::Text(text) => {
                    log::info!("Received WebSocket message: {}", text);
                    if session.text(format!("Echo: {}", text)).await.is_err() {
                        return;
                    }
                }
                Message::Close(_) => {
                    log::info!("WebSocket connection closed");
                    return;
                }
                _ => {}
            }
        }
    });
    
    Ok(response)
}
