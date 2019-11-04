const root = process.env.VUE_APP_API_ROOT_URL;

function urlForPath(path, param) {
  if (!root.endsWith("/")) {
    throw new Error("VUE_APP_API_ROOT_URL must ends with /");
  }
  if (param == undefined || param == "") {
    return root + path;
  }
  return root + path + "/" + param;
}

function messageUrl(token = "") {
  return urlForPath("message", token);
}
function sceneUrl(scene_id = "") {
  return urlForPath("scene", scene_id);
}

export const urls = {
  messageUrl,
  sceneUrl
};
