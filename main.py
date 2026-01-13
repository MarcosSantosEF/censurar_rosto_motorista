import cv2
import mediapipe as mp
import numpy as np
import time
import itertools

INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO = "output.mp4"
LOGO_PATH = "logo.png"

NOME_MOTORISTA = "Marcos Martins dos Santos"
CPF_MOTORISTA  = "000.000.000-00"

PIXEL_SIZE = 22
EXPAND = 0.40
FACE_TTL = 10
IOU_THRESHOLD = 0.3

# =============================
# MediaPipe
# =============================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=10,
    refine_landmarks=True,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4
)

cap = cv2.VideoCapture(INPUT_VIDEO)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = cap.get(cv2.CAP_PROP_FPS)
total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

# =============================
# Logo (carregada 1x)
# =============================
logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
assert logo is not None, "❌ Logo não encontrada"

logo_h, logo_w = logo.shape[:2]
logo_scale = 0.15  # 15% da largura do vídeo
new_w = int(width * logo_scale)
new_h = int((new_w / logo_w) * logo_h)
logo = cv2.resize(logo, (new_w, new_h))

# =============================
# Utils
# =============================
start = time.time()
frame_idx = 0
next_id = itertools.count()
faces = {}

def expand_box(x, y, w, h):
    cx, cy = x + w//2, y + h//2
    nw, nh = int(w*(1+EXPAND)), int(h*(1+EXPAND))
    nx = max(0, cx - nw//2)
    ny = max(0, cy - nh//2)
    return nx, ny, min(nw, width-nx), min(nh, height-ny)

def iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax2, ay2 = ax+aw, ay+ah
    bx2, by2 = bx+bw, by+bh

    inter_x1, inter_y1 = max(ax,bx), max(ay,by)
    inter_x2, inter_y2 = min(ax2,bx2), min(ay2,by2)

    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0

    inter = (inter_x2-inter_x1)*(inter_y2-inter_y1)
    union = aw*ah + bw*bh - inter
    return inter / union


def draw_multiline_text(frame, text, x, y, max_width, font, font_scale, color, thickness, line_spacing):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        (w, h), _ = cv2.getTextSize(test, font, font_scale, thickness)

        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    for i, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (x, y + i * line_spacing),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )

    return y + len(lines) * line_spacing

def draw_logo(frame):
    margin = 20
    y = margin
    x = width - logo.shape[1] - margin

    # 🔹 Logo
    if logo.shape[2] == 4:
        alpha = logo[:,:,3] / 255.0
        for c in range(3):
            frame[y:y+logo.shape[0], x:x+logo.shape[1], c] = (
                alpha * logo[:,:,c] +
                (1-alpha) * frame[y:y+logo.shape[0], x:x+logo.shape[1], c]
            )
    else:
        frame[y:y+logo.shape[0], x:x+logo.shape[1]] = logo

    # 🔹 Texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.30
    thickness = 2
    line_spacing = 50

    text_x = x
    text_y = y + logo.shape[0] + 40
    max_text_width = width - x - margin  # nunca sai da tela

    # Nome (com quebra)
    next_y = draw_multiline_text(
        frame,
        f"Enviado para: {NOME_MOTORISTA}",
        text_x,
        text_y,
        max_text_width,
        font,
        font_scale,
        (255,255,255),
        thickness,
        line_spacing
    )

    # CPF
    cv2.putText(
        frame,
        f"CPF: {CPF_MOTORISTA}",
        (text_x, next_y + 10),
        font,
        font_scale,
        (255,255,255),
        thickness,
        cv2.LINE_AA
    )


# =============================
# LOOP
# =============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    detections = []

    if results.multi_face_landmarks:
        for face in results.multi_face_landmarks:
            pts = np.array([
                (int(lm.x*width), int(lm.y*height))
                for lm in face.landmark
            ])
            x,y,w,h = cv2.boundingRect(pts)
            detections.append(expand_box(x,y,w,h))

    updated = {}
    used = set()

    for fid, (fx,fy,fw,fh,_) in faces.items():
        best_iou = 0
        best_det = None

        for i, det in enumerate(detections):
            if i in used:
                continue
            score = iou((fx,fy,fw,fh), det)
            if score > best_iou:
                best_iou = score
                best_det = i

        if best_iou > IOU_THRESHOLD:
            updated[fid] = [*detections[best_det], FACE_TTL]
            used.add(best_det)
        else:
            faces[fid][4] -= 1
            if faces[fid][4] > 0:
                updated[fid] = faces[fid]

    for i, det in enumerate(detections):
        if i not in used:
            updated[next(next_id)] = [*det, FACE_TTL]

    faces = updated

    # 🎭 Blur
    for x,y,w,h,_ in faces.values():
        roi = frame[y:y+h, x:x+w]
        if roi.size == 0:
            continue
        small = cv2.resize(roi, (PIXEL_SIZE,PIXEL_SIZE))
        frame[y:y+h, x:x+w] = cv2.resize(
            small, (w,h), interpolation=cv2.INTER_NEAREST
        )

    # 🖼️ Logo + Texto
    draw_logo(frame)

    out.write(frame)

    elapsed = time.time()-start
    fps_real = frame_idx/elapsed
    eta = (total-frame_idx)/fps_real if fps_real>0 else 0

    print(
        f"\rFrame {frame_idx}/{total} | "
        f"{fps_real:.1f} FPS | ETA {int(eta//60):02d}:{int(eta%60):02d}",
        end=""
    )

cap.release()
out.release()
print("\n✅ Vídeo processado com logo e identificação")
