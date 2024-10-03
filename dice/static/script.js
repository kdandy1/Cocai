import * as THREE from 'three'
import * as CANNON from 'https://cdn.jsdelivr.net/npm/cannon-es@0.20.0/dist/cannon-es.min.js'
import CameraControls from 'https://cdn.jsdelivr.net/npm/camera-controls@2.9.0/+esm'
import {
  DiceManager,
  DiceD4,
  DiceD6,
  DiceD8,
  DiceD10,
  DiceD12,
  DiceD20
} from './dice.js'

CameraControls.install({ THREE })

/** Copied from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random#getting_a_random_number_between_two_values */
function getRandomArbitrary (min, max) {
  return Math.random() * (max - min) + min
}

const scene = new THREE.Scene()
// "[FogExp2] gives a clear view near the camera and a faster than exponentially densening fog farther from the camera"
// https://threejs.org/docs/#api/en/scenes/FogExp2
scene.fog = new THREE.FogExp2(0xffffff, 0.00025)
// "The X axis is red. The Y axis is green. The Z axis is blue."
// https://threejs.org/docs/#api/en/helpers/AxesHelper
scene.add(new THREE.AxesHelper(100))

// Initialize the renderer.
const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
document.body.appendChild(renderer.domElement)

/* "The Cannon physics library is ideal for simulating rigid bodies." https://sbcode.net/threejs/physics-cannonjs/ */
const world = new CANNON.World()
world.gravity.set(0, -9.82 * 50, 0)
/* "Broad phase is the first step in the collision detection process, where it identifies which objects might be
    colliding. It's called broad phase because it uses bounding boxes that are aligned with the axes, and only reports
    potential collisions. The next step in the process, called narrow phase, is when the actual collisions are detected
    and resolved." (Gemini-generated)
    See https://pmndrs.github.io/cannon-es/docs/classes/Broadphase.html */
world.broadphase = new CANNON.NaiveBroadphase()
world.solver.iterations = 16

// Floor.
const floorBody = new CANNON.Body({
  mass: 0,
  shape: new CANNON.Plane(),
  material: DiceManager.floorBodyMaterial
})
floorBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2)
world.addBody(floorBody)

DiceManager.setWorld(world)

const diceArray = []
diceOptions.forEach((option, index) => { // eslint-disable-line no-undef
  const [type, value] = option

  let dice
  switch (type) {
    case 'd4':
      dice = new DiceD4({ backColor: '#ffffff' })
      break
    case 'd6':
      dice = new DiceD6({ backColor: '#ffffff' })
      break
    case 'd8':
      dice = new DiceD8({ backColor: '#ffffff' })
      break
    case 'd10':
      dice = new DiceD10({ backColor: '#ffffff' })
      break
    case 'd12':
      dice = new DiceD12({ backColor: '#ffffff' })
      break
    case 'd20':
      dice = new DiceD20({ backColor: '#ffffff' })
      break
    default:
      break
  }

  if (dice) {
    // TODO: Update the material. https://threejs.org/examples/#webgl_materials_physical_clearcoat
    dice
      .getObject()
      .position.set(
        index * 200 + 100,
        200 + getRandomArbitrary(-100, 100),
        getRandomArbitrary(-100, 100)
      )
    // Ranges of Euler angles (ϕ,θ,ψ): [0,2π)×[−π/2,π/2]×[0,2π).
    // https://motion.cs.illinois.edu/RoboticSystems/3DRotations.html
    dice
      .getObject()
      .rotation.set(
        getRandomArbitrary(0, 2) * Math.PI,
        getRandomArbitrary(-0.5, 0.5) * Math.PI,
        getRandomArbitrary(0, 2) * Math.PI
      )

    dice.getObject().body.velocity.set(
      getRandomArbitrary(-100, 100),
      // Doesn't make sense to have an initial velocity going upwards.
      getRandomArbitrary(0, 100),
      getRandomArbitrary(-100, 100)
    )

    dice
      .getObject()
      .body.angularVelocity.set(
        getRandomArbitrary(-5, 5),
        getRandomArbitrary(-5, 5),
        getRandomArbitrary(-5, 5)
      )
    dice.getObject().receiveShadow = true

    dice.updateBodyFromMesh()

    setTimeout(() => scene.add(dice.getObject()), index * 100 /* ms */)
    // We use `forEach` + `push` instead of `map`, because `dice` may be `undefined`.
    diceArray.push({ dice, value })
  }
})
DiceManager.prepareValues(diceArray)

// https://threejs.org/docs/#api/en/cameras/PerspectiveCamera
const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  100000
)
camera.up = new THREE.Vector3(0, 1, 0)
scene.add(camera)

// Initialize camera controls, so that you can use your mouse on the scene to tilt & pan the camera.
const clock = new THREE.Clock()
const cameraControls = new CameraControls(camera, renderer.domElement)
// Use `cameraControls.setLookAt` instead of `camera.position` and `camera.lookAt`.
cameraControls.setLookAt(
  diceArray.length * 100,
  1000,
  500,
  diceArray.length * 100,
  100,
  100,
  false
)

const skyBoxGeometry = new THREE.BoxGeometry(10000, 10000, 10000)
const skyBoxMaterial = new THREE.MeshPhongMaterial({
  color: 0x444444,
  side: THREE.BackSide
})
const skyBox = new THREE.Mesh(skyBoxGeometry, skyBoxMaterial)
scene.add(skyBox)

/** We want to render a plane as the "ground" of our scene, where dices will bounce off and settle still.
   Note how this is different from the `floorBody` that we added to the Cannon.js world.
   The `ground` mesh is a visual representation of the ground, while the `floorBody` is a physical representation of the ground. */
function createGround () {
  const groundGeometry = new THREE.PlaneGeometry(
    // We want the ground to be wide enough to encompass all dices...
    diceArray.length * 300,
    // ... but still have a fixed height.
    800)
  // Create a material for the ground.
  const groundMaterial = new THREE.MeshStandardMaterial({ bumpScale: 20 })
  /* I really like the wooden texture from the three.js examples, so I'm going to use it here.
       https://github.com/mrdoob/three.js/blob/master/examples/webgl_lights_physical.html */
  function applyCommonSettingsToTextureMap (map) {
    map.wrapS = THREE.RepeatWrapping
    map.wrapT = THREE.RepeatWrapping
    map.anisotropy = 4
    map.repeat.set(1, 1)
    map.colorSpace = THREE.SRGBColorSpace
    groundMaterial.needsUpdate = true
  }
  const textureLoader = new THREE.TextureLoader()
  textureLoader.load(
    'https://threejs.org/examples/textures/hardwood2_diffuse.jpg',
    (map) => {
      groundMaterial.map = map
      applyCommonSettingsToTextureMap(map)
    }
  )
  textureLoader.load(
    'https://threejs.org/examples/textures/hardwood2_bump.jpg',
    (map) => {
      groundMaterial.bumpMap = map
      applyCommonSettingsToTextureMap(map)
    }
  )
  textureLoader.load(
    'https://threejs.org/examples/textures/hardwood2_roughness.jpg',
    (map) => {
      groundMaterial.roughnessMap = map
      applyCommonSettingsToTextureMap(map)
    }
  )

  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  scene.add(ground)
  ground.position.set(diceArray.length * 100, 0, 0)
  ground.rotation.set(-Math.PI / 2, 0, 0)
  ground.receiveShadow = true
  groundGeometry.computeBoundingSphere()
  return ground
}
const ground = createGround()
const boundingSphere = ground.geometry.boundingSphere

// ====================================================== Lights ======================================================
// --------------------------------- Ambient lights make un-illuminated areas visible ---------------------------------
const ambient = new THREE.AmbientLight(0xffffff, 0.3)
scene.add(ambient)
// --------------------------------------- Directional lights simulate sunlight ---------------------------------------
const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
// We want it to be positioned in the sky...
directionalLight.position.set(-1000, 2000, 2000)
// ... and point at the ground.
directionalLight.target = ground
// - - - - - - - - - - - - - - - - - - - - - We want the light to cast shadows - - - - - - - - - - - - - - - - - - - -
directionalLight.castShadow = true
/* Shadows casted by a directional light is determined with a camera. We want to ensure that it encompasses the
   entire ground, but not any bigger (to save computational resources).
   We do so by calculating the bounding sphere of the ground and then encompassing the camera's frustum around it.
   The use of a bounding sphere is intuitive, because we are dealing with the problem of a beam (the light) and a
   volume (the ground and all dices on it). */
directionalLight.shadow.camera.top = boundingSphere.radius
directionalLight.shadow.camera.bottom = -boundingSphere.radius
directionalLight.shadow.camera.left = -boundingSphere.radius
directionalLight.shadow.camera.right = boundingSphere.radius
const distance = directionalLight.position.distanceTo(ground.position)
directionalLight.shadow.camera.near = distance - boundingSphere.radius
directionalLight.shadow.camera.far = distance + boundingSphere.radius
directionalLight.shadow.camera.lookAt(ground.position)
scene.add(directionalLight)
// =====================================================^ Lights ^=====================================================

function animate () {
  world.step(1.0 / 60.0)
  diceArray.forEach((diceObj) => {
    diceObj.dice.updateMeshFromBody()
  })

  const delta = clock.getDelta()
  cameraControls.update(delta)
  requestAnimationFrame(animate) // eslint-disable-line no-undef

  renderer.render(scene, camera)
}

requestAnimationFrame(animate) // eslint-disable-line no-undef
